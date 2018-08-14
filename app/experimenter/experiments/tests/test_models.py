import datetime

from django.conf import settings
from django.test import TestCase

from experimenter.experiments.models import (
    Experiment,
    ExperimentVariant,
    ExperimentChangeLog,
)
from experimenter.experiments.tests.factories import (
    ExperimentFactory,
    ExperimentChangeLogFactory,
    ExperimentCommentFactory,
)


class TestExperimentManager(TestCase):

    def test_queryset_annotated_with_latest_change(self):
        now = datetime.datetime.now()
        experiment1 = ExperimentFactory.create_with_variants()
        experiment2 = ExperimentFactory.create_with_variants()

        ExperimentChangeLogFactory.create(
            experiment=experiment1,
            old_status=None,
            new_status=Experiment.STATUS_DRAFT,
            changed_on=(now - datetime.timedelta(days=2)),
        )

        ExperimentChangeLogFactory.create(
            experiment=experiment2,
            old_status=None,
            new_status=Experiment.STATUS_DRAFT,
            changed_on=(now - datetime.timedelta(days=1)),
        )

        self.assertEqual(
            list(Experiment.objects.order_by("-latest_change")),
            [experiment2, experiment1],
        )

        ExperimentChangeLogFactory.create(
            experiment=experiment1,
            old_status=experiment1.status,
            new_status=Experiment.STATUS_REVIEW,
        )

        self.assertEqual(
            list(Experiment.objects.order_by("-latest_change")),
            [experiment1, experiment2],
        )


class TestExperimentModel(TestCase):

    def test_start_date_returns_proposed_start_date_if_change_is_missing(self):
        experiment = ExperimentFactory.create_with_variants()
        self.assertEqual(experiment.start_date, experiment.proposed_start_date)

    def test_end_date_returns_proposed_end_date_if_change_is_missing(self):
        experiment = ExperimentFactory.create_with_variants()
        self.assertEqual(experiment.end_date, experiment.proposed_end_date)

    def test_start_date_returns_datetime_if_change_exists(self):
        change = ExperimentChangeLogFactory.create(
            old_status=Experiment.STATUS_ACCEPTED,
            new_status=Experiment.STATUS_LIVE,
        )
        self.assertEqual(
            change.experiment.start_date, change.changed_on.date()
        )

    def test_end_date_returns_datetime_if_change_exists(self):
        change = ExperimentChangeLogFactory.create(
            old_status=Experiment.STATUS_LIVE,
            new_status=Experiment.STATUS_COMPLETE,
        )
        self.assertEqual(change.experiment.end_date, change.changed_on.date())

    def test_control_property_returns_experiment_control(self):
        experiment = ExperimentFactory.create_with_variants()
        control = ExperimentVariant.objects.get(
            experiment=experiment, is_control=True
        )
        self.assertEqual(experiment.control, control)

    def test_experiment_is_editable_when_is_draft(self):
        experiment = ExperimentFactory.create_with_status(
            Experiment.STATUS_DRAFT
        )
        self.assertTrue(experiment.is_editable)

    def test_experiment_is_editable_when_is_in_review(self):
        experiment = ExperimentFactory.create_with_status(
            Experiment.STATUS_REVIEW
        )
        self.assertTrue(experiment.is_editable)

    def test_experient_is_not_editable_after_review(self):
        all_statuses = set([status[0] for status in Experiment.STATUS_CHOICES])
        editable_statuses = set(
            [Experiment.STATUS_DRAFT, Experiment.STATUS_REVIEW]
        )
        for status in all_statuses - editable_statuses:
            experiment = ExperimentFactory.create_with_status(status)
            self.assertFalse(experiment.is_editable)

    def test_experiment_is_not_begun(self):
        statuses = (
            Experiment.STATUS_DRAFT,
            Experiment.STATUS_REVIEW,
            Experiment.STATUS_REJECTED,
        )

        for status in statuses:
            experiment = ExperimentFactory.create_with_status(status)
            self.assertFalse(experiment.is_begun)

    def test_experiment_is_begun(self):
        for status in Experiment.STATUS_LIVE, Experiment.STATUS_COMPLETE:
            experiment = ExperimentFactory.create_with_status(status)
            self.assertTrue(experiment.is_begun)

    def test_overview_is_not_complete_when_not_saved(self):
        experiment = ExperimentFactory.build()
        self.assertFalse(experiment.completed_overview)

    def test_overview_is_complete_when_saved(self):
        experiment = ExperimentFactory.create()
        self.assertTrue(experiment.completed_overview)

    def test_variants_is_not_complete_when_no_variants_saved(self):
        experiment = ExperimentFactory.create()
        self.assertFalse(experiment.completed_variants)

    def test_variants_is_complete_when_variants_saved(self):
        experiment = ExperimentFactory.create_with_variants()
        self.assertTrue(experiment.completed_variants)

    def test_objectives_is_not_complete_with_still_default(self):
        experiment = ExperimentFactory.create(
            objectives=Experiment.OBJECTIVES_DEFAULT,
            analysis=Experiment.ANALYSIS_DEFAULT,
        )
        self.assertFalse(experiment.completed_objectives)

    def test_objectives_is_complete_with_non_defaults(self):
        experiment = ExperimentFactory.create(
            objectives="Some objectives!", analysis="Some analysis!"
        )
        self.assertTrue(experiment.completed_objectives)

    def test_risk_questions_returns_a_tuple(self):
        experiment = ExperimentFactory.create(
            risk_partner_related=False,
            risk_brand=True,
            risk_fast_shipped=False,
            risk_confidential=True,
            risk_release_population=False,
        )
        self.assertEqual(
            experiment._risk_questions, (False, True, False, True, False)
        )

    def test_risk_not_completed_when_risk_questions_not_answered(self):
        experiment = ExperimentFactory.create(
            risk_partner_related=None,
            risk_brand=None,
            risk_fast_shipped=None,
            risk_confidential=None,
            risk_release_population=None,
            testing="A test plan!",
        )
        self.assertFalse(experiment.completed_risks)

    def test_risk_not_completed_when_risk_questions_answered_not_testing(self):
        experiment = ExperimentFactory.create(
            risk_partner_related=False,
            risk_brand=True,
            risk_fast_shipped=False,
            risk_confidential=True,
            risk_release_population=False,
            testing=Experiment.TESTING_DEFAULT,
        )
        self.assertFalse(experiment.completed_risks)

    def test_risk_completed_when_risk_questions_and_testing_completed(self):
        experiment = ExperimentFactory.create(
            risk_partner_related=False,
            risk_brand=True,
            risk_fast_shipped=False,
            risk_confidential=True,
            risk_release_population=False,
            testing="A test plan!",
        )
        self.assertTrue(experiment.completed_risks)

    def test_is_not_launchable_when_not_all_sections_completed(self):
        experiment = ExperimentFactory.create()
        self.assertFalse(experiment.is_ready_for_review)

    def test_is_ready_for_review_when_all_sections_complete(self):
        experiment = ExperimentFactory.create_with_variants()
        self.assertTrue(experiment.is_ready_for_review)

    def test_is_not_high_risk_if_no_risk_questions_are_true(self):
        experiment = ExperimentFactory.create(
            risk_partner_related=False,
            risk_brand=False,
            risk_fast_shipped=False,
            risk_confidential=False,
            risk_release_population=False,
        )
        self.assertFalse(experiment.is_high_risk)

    def test_is_high_risk_if_any_risk_questions_are_true(self):
        risk_fields = (
            "risk_partner_related",
            "risk_brand",
            "risk_fast_shipped",
            "risk_confidential",
            "risk_release_population",
        )

        for true_risk_field in risk_fields:
            instance_risk_fields = {field: False for field in risk_fields}
            instance_risk_fields[true_risk_field] = True

            experiment = ExperimentFactory.create(**instance_risk_fields)
            self.assertTrue(experiment.is_high_risk)

    def test_experiment_population_returns_correct_string(self):
        experiment = ExperimentFactory(
            population_percent="0.5",
            firefox_version="57.0",
            firefox_channel="Nightly",
        )
        self.assertEqual(experiment.population, "0.5% of Nightly Firefox 57.0")

    def test_test_tube_link_is_correct(self):
        experiment = ExperimentFactory.create(slug="experiment")
        self.assertEqual(
            experiment.test_tube_url,
            "https://firefox-test-tube.herokuapp.com/experiments/experiment/",
        )

    def test_accept_url_is_correct(self):
        experiment = ExperimentFactory.create(slug="experiment")
        self.assertEqual(
            experiment.accept_url,
            "https://localhost/api/v1/experiments/experiment/accept/",
        )

    def test_reject_url_is_correct(self):
        experiment = ExperimentFactory.create(slug="experiment")
        self.assertEqual(
            experiment.reject_url,
            "https://localhost/api/v1/experiments/experiment/reject/",
        )

    def test_experiment_missing_bugzilla_id_returns_url_None(self):
        experiment = ExperimentFactory.create_with_status(
            Experiment.STATUS_DRAFT, bugzilla_id=None
        )
        self.assertEqual(experiment.bugzilla_url, None)

    def test_bugzilla_url_is_correct(self):
        experiment = ExperimentFactory.create_with_status(
            Experiment.STATUS_DRAFT, bugzilla_id="1234"
        )
        self.assertEqual(
            experiment.bugzilla_url,
            settings.BUGZILLA_DETAIL_URL.format(id=experiment.bugzilla_id),
        )

    def test_completed_required_reviews_false_when_reviews_not_complete(self):
        experiment = ExperimentFactory.create()
        self.assertFalse(experiment.completed_required_reviews)

    def test_completed_required_reviews_true_when_reviews_complete(self):
        experiment = ExperimentFactory.create(
            review_phd=True,
            review_science=True,
            review_peer=True,
            review_relman=True,
            review_qa=True,
        )
        self.assertTrue(experiment.completed_required_reviews)


class TestExperimentChangeLog(TestCase):

    def test_latest_returns_most_recent_changelog(self):
        now = datetime.datetime.now()
        experiment = ExperimentFactory.create_with_variants()

        changelog1 = ExperimentChangeLogFactory.create(
            experiment=experiment,
            old_status=None,
            new_status=Experiment.STATUS_DRAFT,
            changed_on=(now - datetime.timedelta(days=2)),
        )

        self.assertEqual(experiment.changes.latest(), changelog1)

        changelog2 = ExperimentChangeLogFactory.create(
            experiment=experiment,
            old_status=Experiment.STATUS_DRAFT,
            new_status=Experiment.STATUS_REVIEW,
            changed_on=(now - datetime.timedelta(days=1)),
        )

        self.assertEqual(experiment.changes.latest(), changelog2)

    def test_pretty_status_created_draft(self):
        experiment = ExperimentFactory.create_with_variants()

        for old_status in ExperimentChangeLog.PRETTY_STATUS_LABELS.keys():
            for new_status in ExperimentChangeLog.PRETTY_STATUS_LABELS[
                old_status
            ].keys():
                expected_label = ExperimentChangeLog.PRETTY_STATUS_LABELS[
                    old_status
                ][new_status]

                changelog = ExperimentChangeLogFactory.create(
                    experiment=experiment,
                    old_status=old_status,
                    new_status=new_status,
                )
                self.assertEqual(changelog.pretty_status, expected_label)


class TestExperimentComments(TestCase):

    def test_manager_returns_sections(self):
        experiment = ExperimentFactory.create_with_status(
            Experiment.STATUS_DRAFT
        )
        risk_comment = ExperimentCommentFactory.create(
            experiment=experiment, section=Experiment.SECTION_RISKS
        )
        testing_comment = ExperimentCommentFactory.create(
            experiment=experiment, section=Experiment.SECTION_TESTING
        )
        self.assertIn(
            risk_comment,
            experiment.comments.sections[experiment.SECTION_RISKS],
        )
        self.assertIn(
            testing_comment,
            experiment.comments.sections[experiment.SECTION_TESTING],
        )
        self.assertNotIn(
            risk_comment,
            experiment.comments.sections[experiment.SECTION_TESTING],
        )
        self.assertNotIn(
            testing_comment,
            experiment.comments.sections[experiment.SECTION_RISKS],
        )
