rm -f beam.pot
touch beam.pot
xgettext --sort-output --language=Python --keyword=_ --output=beam.pot ../*.py

for loc in fr_FR en_US; do
    msgmerge --update --add-location --sort-output ${loc}.po beam.pot
done
