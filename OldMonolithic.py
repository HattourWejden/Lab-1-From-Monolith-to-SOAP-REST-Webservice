import os
import sys
from decimal import Decimal, InvalidOperation

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView
)

from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker


DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg2://inventory:inventory@localhost:5432/inventory"
)

engine = create_engine(DATABASE_URL, echo=False)  # set echo=True for SQL logs
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

    def __repr__(self):
        return f"Product(id={self.id}, name={self.name}, quantity={self.quantity}, price={self.price})"

Base.metadata.create_all(engine)

def create_product(name: str, quantity: int, price: float):
    if quantity < 0 or price < 0:
        raise ValueError("Quantity and price must be >= 0")
    session = SessionLocal()
    try:
        product = Product(name=name, quantity=quantity, price=price)
        session.add(product)
        session.commit()
        session.refresh(product)
        return product
    finally:
        session.close()

def read_all_products():
    session = SessionLocal()
    try:
        return session.query(Product).order_by(Product.id).all()
    finally:
        session.close()

def update_product(product_id: int, name=None, quantity=None, price=None):
    session = SessionLocal()
    try:
        product = session.query(Product).filter_by(id=product_id).first()
        if not product:
            return None
        if name is not None and name != "":
            product.name = name
        if quantity is not None:
            if quantity < 0:
                raise ValueError("Quantity must be >= 0")
            product.quantity = quantity
        if price is not None:
            if price < 0:
                raise ValueError("Price must be >= 0")
            product.price = price
        session.commit()
        session.refresh(product)
        return product
    finally:
        session.close()

def delete_product(product_id: int):
    session = SessionLocal()
    try:
        product = session.query(Product).filter_by(id=product_id).first()
        if not product:
            return None
        session.delete(product)
        session.commit()
        return product
    finally:
        session.close()

class InventoryApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DataMart Inventory - Monolithic")
        self.setMinimumSize(700, 400)
        self.init_ui()
        self.refresh_table()

    def init_ui(self):
       
        self.id_label = QLabel("ID (for update/delete):")
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("Leave empty to create new product")

        self.name_label = QLabel("Name:")
        self.name_input = QLineEdit()

        self.qty_label = QLabel("Quantity:")
        self.qty_input = QLineEdit()

        self.price_label = QLabel("Price:")
        self.price_input = QLineEdit()

        self.create_btn = QPushButton("Create")
        self.create_btn.clicked.connect(self.on_create)

        self.update_btn = QPushButton("Update")
        self.update_btn.clicked.connect(self.on_update)

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self.on_delete)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_table)

       
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Quantity", "Price"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        form_layout = QHBoxLayout()
        form_left = QVBoxLayout()
        form_right = QVBoxLayout()

        form_left.addWidget(self.id_label)
        form_left.addWidget(self.id_input)
        form_left.addWidget(self.name_label)
        form_left.addWidget(self.name_input)

        form_right.addWidget(self.qty_label)
        form_right.addWidget(self.qty_input)
        form_right.addWidget(self.price_label)
        form_right.addWidget(self.price_input)

        form_layout.addLayout(form_left)
        form_layout.addLayout(form_right)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.create_btn)
        btn_layout.addWidget(self.update_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.refresh_btn)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addLayout(btn_layout)
        main_layout.addWidget(self.table)

        self.setLayout(main_layout)

    def show_error(self, message: str):
        QMessageBox.critical(self, "Error", message)

    def show_info(self, message: str):
        QMessageBox.information(self, "Info", message)

    def parse_int(self, text: str):
        text = text.strip()
        if text == "":
            return None
        try:
            val = int(text)
            return val
        except ValueError:
            raise ValueError("Expected integer value")

    def parse_decimal(self, text: str):
        text = text.strip()
        if text == "":
            return None
        try:
            d = Decimal(text)
            return float(d)
        except (InvalidOperation, ValueError):
            raise ValueError("Expected numeric price (e.g. 12.34)")


    def on_create(self):
        try:
            name = self.name_input.text().strip()
            if not name:
                raise ValueError("Name is required")

            quantity = self.parse_int(self.qty_input.text())
            if quantity is None:
                raise ValueError("Quantity is required")

            price = self.parse_decimal(self.price_input.text())
            if price is None:
                raise ValueError("Price is required")

            product = create_product(name, quantity, price)
            self.show_info(f"Created product with ID {product.id}")
            self.clear_inputs()
            self.refresh_table()

        except Exception as e:
            self.show_error(str(e))

    def on_update(self):
        try:
            pid = self.parse_int(self.id_input.text())
            if pid is None:
                raise ValueError("ID is required for update")

            name = self.name_input.text().strip() or None
            quantity = None
            price = None

            if self.qty_input.text().strip() != "":
                quantity = self.parse_int(self.qty_input.text())

            if self.price_input.text().strip() != "":
                price = self.parse_decimal(self.price_input.text())

            updated = update_product(pid, name=name, quantity=quantity, price=price)
            if not updated:
                raise ValueError(f"No product with ID {pid}")
            self.show_info(f"Updated product ID {pid}")
            self.clear_inputs()
            self.refresh_table()
        except Exception as e:
            self.show_error(str(e))

    def on_delete(self):
        try:
            pid = self.parse_int(self.id_input.text())
            if pid is None:
                raise ValueError("ID is required for delete")
            deleted = delete_product(pid)
            if not deleted:
                raise ValueError(f"No product with ID {pid}")
            self.show_info(f"Deleted product ID {pid}")
            self.clear_inputs()
            self.refresh_table()
        except Exception as e:
            self.show_error(str(e))

    def clear_inputs(self):
        self.id_input.clear()
        self.name_input.clear()
        self.qty_input.clear()
        self.price_input.clear()

    def refresh_table(self):
        products = read_all_products()
        self.table.setRowCount(len(products))
        for row, p in enumerate(products):
            self.table.setItem(row, 0, QTableWidgetItem(str(p.id)))
            self.table.setItem(row, 1, QTableWidgetItem(p.name))
            self.table.setItem(row, 2, QTableWidgetItem(str(p.quantity)))
            self.table.setItem(row, 3, QTableWidgetItem(f"{p.price:.2f}"))

def main():
    app = QApplication(sys.argv)
    window = InventoryApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
