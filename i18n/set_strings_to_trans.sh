POFILES="fr_FR en_US"
FINALNAME=beam.mo

for i in $POFILES; do
	mkdir -p $i/LC_MESSAGES
	msgfmt --output-file=$i/LC_MESSAGES/$FINALNAME $i.po
done 
