TRUNCATE TABLE aers.demo ;

LOAD DATA INFILE '/tmp/DEMO10Q1.TXT' REPLACE INTO TABLE aers.demo FIELDS TERMINATED BY '$' IGNORE 1 LINES;
 
LOAD DATA INFILE '/tmp/DEMO10Q2.TXT' REPLACE INTO TABLE aers.demo FIELDS TERMINATED BY '$' IGNORE 1 LINES;

LOAD DATA INFILE '/tmp/DEMO10Q3.TXT' REPLACE INTO TABLE aers.demo FIELDS TERMINATED BY '$' IGNORE 1 LINES;

LOAD DATA INFILE '/tmp/DEMO10Q4.TXT' REPLACE INTO TABLE aers.demo FIELDS TERMINATED BY '$' IGNORE 1 LINES;

LOAD DATA INFILE '/tmp/DEMO11Q1.TXT' REPLACE INTO TABLE aers.demo FIELDS TERMINATED BY '$' IGNORE 1 LINES;

LOAD DATA INFILE '/tmp/DEMO11Q2.TXT' REPLACE INTO TABLE aers.demo FIELDS TERMINATED BY '$' IGNORE 1 LINES;


TRUNCATE TABLE aers.drug ;

LOAD DATA INFILE '/tmp/DRUG10Q1.TXT' REPLACE INTO TABLE aers.drug FIELDS TERMINATED BY '$' IGNORE 1 LINES;

LOAD DATA INFILE '/tmp/DRUG10Q2.TXT' REPLACE INTO TABLE aers.drug FIELDS TERMINATED BY '$' IGNORE 1 LINES;

LOAD DATA INFILE '/tmp/DRUG10Q3.TXT' REPLACE INTO TABLE aers.drug FIELDS TERMINATED BY '$' IGNORE 1 LINES;

LOAD DATA INFILE '/tmp/DRUG10Q4.TXT' REPLACE INTO TABLE aers.drug FIELDS TERMINATED BY '$' IGNORE 1 LINES;

LOAD DATA INFILE '/tmp/DRUG11Q1.TXT' REPLACE INTO TABLE aers.drug FIELDS TERMINATED BY '$' IGNORE 1 LINES;

LOAD DATA INFILE '/tmp/DRUG11Q2.TXT' REPLACE INTO TABLE aers.drug FIELDS TERMINATED BY '$' IGNORE 1 LINES;


-- Note that for the below import to work, the '\r' at the end of each line in the INDI??Q?.TXT files needs to be replaced with a '$\r'
TRUNCATE TABLE aers.indi;

LOAD DATA INFILE '/tmp/INDI10Q1.TXT' REPLACE INTO TABLE aers.indi FIELDS TERMINATED BY '$' IGNORE 1 LINES;

LOAD DATA INFILE '/tmp/INDI10Q2.TXT' REPLACE INTO TABLE aers.indi FIELDS TERMINATED BY '$' IGNORE 1 LINES;

LOAD DATA INFILE '/tmp/INDI10Q3.TXT' REPLACE INTO TABLE aers.indi FIELDS TERMINATED BY '$' IGNORE 1 LINES;

LOAD DATA INFILE '/tmp/INDI10Q4.TXT' REPLACE INTO TABLE aers.indi FIELDS TERMINATED BY '$' IGNORE 1 LINES;

LOAD DATA INFILE '/tmp/INDI11Q1.TXT' REPLACE INTO TABLE aers.indi FIELDS TERMINATED BY '$' IGNORE 1 LINES;

LOAD DATA INFILE '/tmp/INDI11Q2.TXT' REPLACE INTO TABLE aers.indi FIELDS TERMINATED BY '$' IGNORE 1 LINES;



TRUNCATE TABLE aers.outc;

LOAD DATA INFILE '/tmp/OUTC10Q1.TXT' REPLACE INTO TABLE aers.outc FIELDS TERMINATED BY '$' IGNORE 1 LINES;

LOAD DATA INFILE '/tmp/OUTC10Q2.TXT' REPLACE INTO TABLE aers.outc FIELDS TERMINATED BY '$' IGNORE 1 LINES;

LOAD DATA INFILE '/tmp/OUTC10Q3.TXT' REPLACE INTO TABLE aers.outc FIELDS TERMINATED BY '$' IGNORE 1 LINES;

LOAD DATA INFILE '/tmp/OUTC10Q4.TXT' REPLACE INTO TABLE aers.outc FIELDS TERMINATED BY '$' IGNORE 1 LINES;

LOAD DATA INFILE '/tmp/OUTC11Q1.TXT' REPLACE INTO TABLE aers.outc FIELDS TERMINATED BY '$' IGNORE 1 LINES;

LOAD DATA INFILE '/tmp/OUTC11Q2.TXT' REPLACE INTO TABLE aers.outc FIELDS TERMINATED BY '$' IGNORE 1 LINES;


TRUNCATE TABLE aers.reac;

LOAD DATA INFILE '/tmp/REAC10Q1.TXT' REPLACE INTO TABLE aers.reac FIELDS TERMINATED BY '$' IGNORE 1 LINES;

LOAD DATA INFILE '/tmp/REAC10Q2.TXT' REPLACE INTO TABLE aers.reac FIELDS TERMINATED BY '$' IGNORE 1 LINES;

LOAD DATA INFILE '/tmp/REAC10Q3.TXT' REPLACE INTO TABLE aers.reac FIELDS TERMINATED BY '$' IGNORE 1 LINES;

LOAD DATA INFILE '/tmp/REAC10Q4.TXT' REPLACE INTO TABLE aers.reac FIELDS TERMINATED BY '$' IGNORE 1 LINES;

LOAD DATA INFILE '/tmp/REAC11Q1.TXT' REPLACE INTO TABLE aers.reac FIELDS TERMINATED BY '$' IGNORE 1 LINES;

LOAD DATA INFILE '/tmp/REAC11Q2.TXT' REPLACE INTO TABLE aers.reac FIELDS TERMINATED BY '$' IGNORE 1 LINES;


TRUNCATE TABLE aers.ther;

LOAD DATA INFILE '/tmp/THER10Q1.TXT' REPLACE INTO TABLE aers.ther FIELDS TERMINATED BY '$' IGNORE 1 LINES;

LOAD DATA INFILE '/tmp/THER10Q2.TXT' REPLACE INTO TABLE aers.ther FIELDS TERMINATED BY '$' IGNORE 1 LINES;

LOAD DATA INFILE '/tmp/THER10Q3.TXT' REPLACE INTO TABLE aers.ther FIELDS TERMINATED BY '$' IGNORE 1 LINES;

LOAD DATA INFILE '/tmp/THER10Q4.TXT' REPLACE INTO TABLE aers.ther FIELDS TERMINATED BY '$' IGNORE 1 LINES;

LOAD DATA INFILE '/tmp/THER11Q1.TXT' REPLACE INTO TABLE aers.ther FIELDS TERMINATED BY '$' IGNORE 1 LINES;

LOAD DATA INFILE '/tmp/THER11Q2.TXT' REPLACE INTO TABLE aers.ther FIELDS TERMINATED BY '$' IGNORE 1 LINES;



UPDATE aers.demo SET death_dt=NULL WHERE death_dt='0000-00-00';
UPDATE aers.demo SET event_dt=NULL WHERE event_dt='0000-00-00';
UPDATE aers.demo SET mfr_dt=NULL WHERE mfr_dt='0000-00-00';
UPDATE aers.demo SET fda_dt=NULL WHERE fda_dt='0000-00-00';
UPDATE aers.demo SET rept_dt=NULL WHERE rept_dt='0000-00-00';

UPDATE aers.drug SET exp_dt=NULL WHERE exp_dt='0000-00-00';

