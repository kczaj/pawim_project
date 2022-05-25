import datetime
import uuid

from fpdf import FPDF
from datetime import datetime


class Package:

    def __init__(self, sender, recipient, created, package_id, photo=""):
        self.__package_id = package_id
        self.__create_date = created
        self.__sender = sender
        self.__recipient = recipient
        self.__photo = photo

    def generate_and_save(self, path="./"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        self.__add_table_to_pdf(pdf)

        filename = self.__generate_filename(path)
        pdf.output(filename)

        return filename

    def __str__(self):
        return "" + self.__package_id

    def get_created(self):
        return "" + self.__create_date

    def __add_table_to_pdf(self, pdf):
        n_cols = 2
        col_width = (pdf.w - pdf.l_margin - pdf.r_margin) / n_cols
        font_size = pdf.font_size
        n_lines = 6

        pdf.cell(col_width, font_size, "ID", border=1)
        pdf.multi_cell(col_width, font_size, txt=self.__package_id, border=1)
        pdf.ln(0)
        pdf.cell(col_width, n_lines * font_size, "Sender", border=1)
        pdf.multi_cell(col_width, font_size, txt=self.__sender.str_full(), border=1)
        pdf.ln(0)
        pdf.cell(col_width, n_lines * font_size, "Recipient", border=1)
        pdf.multi_cell(col_width, font_size, txt=self.__recipient.str_full(), border=1)
        pdf.ln(0)
        pdf.image(self.__photo, w=2*col_width)

    def __generate_filename(self, path):
        unique_filename = self.__package_id

        return "{}{}.pdf".format(path, unique_filename)


class Person:

    def __init__(self, name: str, surname: str, address, phone_number=""):
        self.__name = name
        self.__surname = surname
        self.__address = address
        self.__phone_number = phone_number

    def get_name(self):
        return self.__name

    def get_surname(self):
        return self.__surname

    def get_fullname(self):
        return "{} {}".format(self.__name, self.__surname)

    def get_address(self):
        return self.__address

    def str_full(self):
        return "{}\n{}\n{}".format(self.get_fullname(), self.__phone_number, self.__address.str_full())


class Address:

    def __init__(self, street: str, number: str, postal_code: str):
        self.__street = street
        self.__number    = number
        self.__postal_code = postal_code

    def get_street(self):
        return self.__street

    def get_city(self):
        return self.__number

    def get_postal_code(self):
        return self.__postal_code

    def str_full(self):
        result = ""
        for field_value in self.__dict__.values():
            result += "\n{}".format(field_value)

        return result
