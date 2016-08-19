#!/bin/bash
for t in $(ls test_*|grep -v [.]); do ./$t; done
