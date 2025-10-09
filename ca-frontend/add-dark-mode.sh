#!/bin/bash

# Dark Mode Enhancement Script
# This script adds dark mode classes to common UI patterns

echo "Adding dark mode support to frontend components..."

# Common patterns to update with dark mode classes
# bg-white -> bg-white dark:bg-gray-800
# text-gray-900 -> text-gray-900 dark:text-white  
# text-gray-600 -> text-gray-600 dark:text-gray-400
# border-gray-200 -> border-gray-200 dark:border-gray-700
# bg-gray-50 -> bg-gray-50 dark:bg-gray-900

find ca-frontend/src -name "*.tsx" -type f -exec sed -i '' \
  -e 's/bg-white\([^-]\)/bg-white dark:bg-gray-800\1/g' \
  -e 's/text-gray-900\([^-]\)/text-gray-900 dark:text-white\1/g' \
  -e 's/text-gray-600\([^-]\)/text-gray-600 dark:text-gray-400\1/g' \
  -e 's/border-gray-200\([^-]\)/border-gray-200 dark:border-gray-700\1/g' \
  -e 's/bg-gray-50\([^-]\)/bg-gray-50 dark:bg-gray-900\1/g' \
  {} \;

echo "Dark mode classes added to common patterns!"
echo "Note: Review the changes and adjust as needed for specific components."