HOME=/Users/jiashen/
for i in $( ls $HOME/Desktop/medi_db/current/ ); do
    mysql -u root -ppassword test < $HOME/Desktop/medi_db/current/$i
done
