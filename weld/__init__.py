import os

from flask import Flask, Blueprint
from weld.app import app


def create_app():
    weld_app = app
    return weld_app