Priečinok obsahuje následné súbory:
	|
	| --- mappings:
	|	|
	|	| --- mapping_parent.json      -> obsahuje mapping, v ktorom tweet ma embednuty parent tweet ak ho ma
	|	| 
	|	| --- mapping_no_parent.json   -> obsahuje mapping, bez embednuteho parent tweetu za to obsahuje parent_id ako ref na parenta
	|
	| --- scripts:
	|	|
	|	| --- decrement.json    -> elasticsearch script na dekrement retweet_countu
	|	|
	|	| --- increment.json    -> elasticsearch script na inkrement retweet_countu
	|	|
	|	| --- dumping.py        -> python skript, ktory vytahuje tweet z postgresu cez ORM v bulk formate
	|	|
	|	| --- el_import_bash.sh -> bash skript, ktory importuje data po 25 000 tweetov
	|
	| --- query:
	|	|
	|	| --- 10 -> obsahuje priecinky 1, 2.1, 3, 4, 5, kde kazdy jeden priecinok obsahuje request aj response v json formate
	|	|
	|	| --- 11 -> obsahuje request aj response v json formate
	|
	|
	| --- dokument -> obsahuje dokument k zadaniu