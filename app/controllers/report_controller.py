from app.controllers.base import Controller
from app.schemas.base import validate
from app.schemas.evaluation_schema import EvaluationInput
from app.schemas.report_schema import ReportContent, ReportInput


class ReportListController(Controller):
    def get(self, request):
        return self.ok(self.services.reports.list(request.user))

    def post(self, request):
        return self.ok(
            self.services.reports.create(
                request.user, validate(ReportInput, request.data)
            ),
            201,
        )


class PendingReportController(Controller):
    def get(self, request):
        return self.ok(self.services.reports.list(request.user, pending=True))


class ReportController(Controller):
    def get(self, request, reportId):
        return self.ok(self.services.reports.get(request.user, reportId))


class ResubmitController(Controller):
    def post(self, request, reportId):
        return self.ok(
            self.services.reports.resubmit(
                request.user, reportId, validate(ReportContent, request.data)
            )
        )


class EvaluationController(Controller):
    def post(self, request, reportId):
        return self.ok(
            self.services.evaluations.evaluate(
                request.user, reportId, validate(EvaluationInput, request.data)
            )
        )


class PublishController(Controller):
    def post(self, request, reportId):
        from app.schemas.base import StrictSerializer

        validate(StrictSerializer, request.data)
        return self.ok(self.services.github.publish(request.user, reportId))
