import sys
from typing import List, Dict, Optional

import requests
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QToolBar, QMessageBox, QInputDialog, QDialog, QListWidget, QListWidgetItem
)

API_BASE = "http://127.0.0.1:8000"


def api_get(path: str, token: str) -> Dict:
    r = requests.get(f"{API_BASE}{path}", headers={"X-Admin-Token": token}, timeout=10)
    if r.status_code >= 400:
        try:
            raise Exception(r.json().get("detail", r.text))
        except Exception:
            raise Exception(r.text)
    return r.json()


def api_post(path: str, token: str, json_body: dict) -> Dict:
    r = requests.post(f"{API_BASE}{path}", headers={"X-Admin-Token": token}, json=json_body, timeout=10)
    if r.status_code >= 400:
        try:
            raise Exception(r.json().get("detail", r.text))
        except Exception:
            raise Exception(r.text)
    return r.json()


def api_delete(path: str, token: str) -> Dict:
    r = requests.delete(f"{API_BASE}{path}", headers={"X-Admin-Token": token}, timeout=10)
    if r.status_code >= 400:
        try:
            raise Exception(r.json().get("detail", r.text))
        except Exception:
            raise Exception(r.text)
    return r.json()


class AdminWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Messenger Admin Panel")
        self.setMinimumSize(980, 620)

        self.token_edit = QLineEdit()
        self.token_edit.setPlaceholderText("ADMIN_TOKEN (по умолчанию admin123)")
        self.token_edit.setEchoMode(QLineEdit.Password)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Поиск пользователя…")
        self.search_edit.textChanged.connect(self._apply_filter)

        self.refresh_btn = QPushButton("Обновить пользователей")
        self.refresh_btn.clicked.connect(self._load_users)

        self.requests_btn = QPushButton("Заявки в друзья")
        self.requests_btn.clicked.connect(self._show_requests)

        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.addWidget(QLabel("🔑 Токен:"))
        toolbar.addWidget(self.token_edit)
        toolbar.addSeparator()
        toolbar.addWidget(self.search_edit)
        toolbar.addSeparator()
        toolbar.addWidget(self.refresh_btn)
        toolbar.addWidget(self.requests_btn)
        self.addToolBar(toolbar)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["ID", "Имя", "Друзья", "Вх. заявки", "Исх. заявки", "Действия"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)

        central = QWidget()
        lay = QVBoxLayout(central)
        lay.addWidget(self.table)
        self.setCentralWidget(central)

        self._data: List[Dict] = []

        # Style (dark)
        self.setStyleSheet(
            """
            QWidget { background:#0b1220; color:#e2e8f0; font-size:14px; }
            QLineEdit { background:#0f172a; border:1px solid #1f2937; border-radius:10px; padding:8px; color:#e2e8f0; }
            QPushButton { background:#6366f1; border:none; padding:8px 10px; border-radius:10px; color:white; font-weight:600; }
            QPushButton:hover { background:#5457ee; }
            QToolBar { background:#0b1220; border:0; spacing:8px; }
            QTableWidget { background:#0f172a; border:1px solid #1f2937; border-radius:10px; }
            QHeaderView::section { background:#111827; color:#cbd5e1; padding:6px; border:none; }
            """
        )

    def _token(self) -> str:
        t = self.token_edit.text().strip()
        return t or "admin123"

    def _apply_filter(self):
        q = self.search_edit.text().strip().lower()
        self.table.setRowCount(0)
        for u in self._data:
            if q and q not in u["username"].lower():
                continue
            self._append_row(u)

    def _append_row(self, u: Dict):
        r = self.table.rowCount()
        self.table.insertRow(r)
        self.table.setItem(r, 0, QTableWidgetItem(str(u.get("id"))))
        self.table.setItem(r, 1, QTableWidgetItem(u.get("username", "")))
        self.table.setItem(r, 2, QTableWidgetItem(str(u.get("friends_count", 0))))
        self.table.setItem(r, 3, QTableWidgetItem(str(u.get("incoming_count", 0))))
        self.table.setItem(r, 4, QTableWidgetItem(str(u.get("outgoing_count", 0))))

        # Actions cell
        cell = QWidget()
        h = QHBoxLayout(cell)
        h.setContentsMargins(0, 0, 0, 0)
        btn_reset = QPushButton("Сброс пароля")
        btn_delete = QPushButton("Удалить")
        btn_delete.setStyleSheet("QPushButton{background:#ef4444;} QPushButton:hover{background:#dc2626}")
        btn_reset.clicked.connect(lambda: self._reset_password(u))
        btn_delete.clicked.connect(lambda: self._delete_user(u))
        h.addWidget(btn_reset)
        h.addWidget(btn_delete)
        h.addStretch(1)
        self.table.setCellWidget(r, 5, cell)

    def _load_users(self):
        try:
            res = api_get("/admin/users", self._token())
            self._data = res.get("users", [])
            self.table.setRowCount(0)
            for u in self._data:
                self._append_row(u)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def _show_requests(self):
        try:
            res = api_get("/admin/requests", self._token())
            reqs = res.get("requests", [])
            dlg = QDialog(self)
            dlg.setWindowTitle("Заявки в друзья")
            v = QVBoxLayout(dlg)
            lst = QListWidget()
            for r in reqs:
                item = QListWidgetItem(f"{r['from_username']} -> {r['to_username']}")
                lst.addItem(item)
            v.addWidget(lst)
            ok = QPushButton("Закрыть")
            ok.clicked.connect(dlg.accept)
            v.addWidget(ok)
            dlg.exec()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def _reset_password(self, u: Dict):
        new_pw, ok = QInputDialog.getText(self, "Сброс пароля", f"Новый пароль для {u['username']}")
        if not ok or not (new_pw or "").strip():
            return
        try:
            api_post("/admin/reset_password", self._token(), {"user_id": u["id"], "new_password": new_pw})
            QMessageBox.information(self, "Готово", "Пароль сброшен")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def _delete_user(self, u: Dict):
        if QMessageBox.question(self, "Удаление", f"Удалить пользователя {u['username']}?") != QMessageBox.Yes:
            return
        try:
            api_delete(f"/admin/users/{u['id']}", self._token())
            self._load_users()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))


def main():
    app = QApplication(sys.argv)
    w = AdminWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
