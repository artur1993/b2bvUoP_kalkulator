#!/bin/bash

# Skrypt do generowania raportu pokrycia kodu dla frontendu (JavaScript/React)

cd frontend
npm test -- --coverage
cd ../..
