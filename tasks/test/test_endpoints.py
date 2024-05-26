from unittest import TestCase
from piccolo.apps.migrations.commands.backwards import run_backwards
from piccolo.apps.migrations.commands.forwards import run_forwards
from piccolo.apps.user.tables import BaseUser
from piccolo.utils.sync import run_sync
from fastapi.testclient import TestClient
from piccolo_api.session_auth.tables import SessionsBase
from app import app
from fastapi import status
from piccolo.testing.model_builder import ModelBuilder
from tasks.tables import Task


class TaskEndpointTestCase(TestCase):
    def setUp(self):
        super().setUp()
        run_sync(run_forwards("all"))
        self.primary_user = ModelBuilder.build_sync(BaseUser, defaults={"active": True})
        self.secondary_user = ModelBuilder.build_sync(
            BaseUser, defaults={"active": True}
        )
        self.primary_user_task = ModelBuilder.build_sync(
            Task, defaults={"assignee_id": self.primary_user.id}
        )
        self.secondary_user_task = ModelBuilder.build_sync(
            Task, defaults={"assignee_id": self.secondary_user.id}
        )

    def _create_user_session(self) -> SessionsBase:
        session = SessionsBase.create_session_sync(self.primary_user.id)
        return session

    def _get_authenticated_client(self) -> TestClient:
        session = self._create_user_session()
        return TestClient(app, cookies={"id": session.token})

    def tearDown(self):
        super().tearDown()
        run_sync(run_backwards("all", auto_agree=True))


class TaskListTestCase(TaskEndpointTestCase):

    def test__when_no_login__endpoint_does_not_list_tasks(self):
        client = TestClient(app)
        response = client.get("/task_manager/tasks")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test__when_client_logged_in__endpoint_lists_users_tasks(self):
        client = self._get_authenticated_client()
        response = client.get("/task_manager/tasks")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        tasks = response.json()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].get("id"), self.primary_user_task.id)


class TaskCreateTestCase(TaskEndpointTestCase):

    def test__when_no_login__cannot_create_new_tasks(self):
        client = TestClient(app)
        response = client.post("/task_manager/tasks", json={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test__when_logged_in__can_create_new_tasks(self):
        client = self._get_authenticated_client()
        initial_count = Task.count().run_sync()
        test_task_name = "Try test application"
        example_data = {
            "name": test_task_name,
            "description": "This is a test of the application",
            "assignee_id": self.primary_user.id,
            "status": "Doing",
            "parent_task": None,
            "date_due": "2024-05-26",
        }
        response = client.post(
            "/task_manager/tasks/",
            json=example_data,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Task.count().run_sync(), initial_count + 1)
        self.assertTrue(Task.exists().where(Task.name == test_task_name).run_sync())


class TaskUpdateTestCase(TaskEndpointTestCase):

    def test__when_no_login__cannot_update_new_tasks(self):
        client = TestClient(app)
        response = client.put(
            f"/task_manager/tasks/{self.primary_user_task.id}/", json={}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test__when_logged_in__can_create_new_tasks(self):
        client = self._get_authenticated_client()
        test_update = "Updated name"
        response = client.put(
            f"/task_manager/tasks/{self.primary_user_task.id}/",
            json={
                "name": test_update,
                "description": "This is an update",
                "assignee_id": self.primary_user.id,
                "status": self.primary_user_task.status,
                "parent_task": self.primary_user_task.parent_task,
                "date_due": "2024-05-26",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Task.exists().where(Task.name == test_update).run_sync())


class TaskDeleteTestCase(TaskEndpointTestCase):

    def test__when_no_login__cannot_delete_existing_tasks(self):
        client = TestClient(app)
        response = client.delete(f"/task_manager/tasks/{self.primary_user_task.id}/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test__when_logged_in__can_delete_existing_tasks(self):
        client = self._get_authenticated_client()
        response = client.delete(
            f"/task_manager/tasks/{self.primary_user_task.id}/",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            Task.exists().where(Task.id == self.primary_user_task.id).run_sync()
        )
