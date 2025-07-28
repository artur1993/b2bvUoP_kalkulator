#!/bin/bash

# Skrypt do generowania raportu pokrycia kodu dla frontendu (JavaScript/React)

cd src/dashboard
npm test -- --coverage
cd ../..
