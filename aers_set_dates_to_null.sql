UPDATE aers.demo SET death_dt=NULL WHERE death_dt='0000-00-00';
UPDATE aers.demo SET event_dt=NULL WHERE event_dt='0000-00-00';
UPDATE aers.demo SET mfr_dt=NULL WHERE mfr_dt='0000-00-00';
UPDATE aers.demo SET fda_dt=NULL WHERE fda_dt='0000-00-00';
UPDATE aers.demo SET rept_dt=NULL WHERE rept_dt='0000-00-00';

SELECT COUNT(*) FROM aers.demo WHERE death_dt='0000-00-00' OR event_dt='0000-00-00' OR mfr_dt='0000-00-00' OR fda_dt='0000-00-00' OR rept_dt='0000-00-00';

UPDATE aers.drug SET exp_dt=NULL WHERE exp_dt='0000-00-00';

SELECT COUNT(*) FROM aers.drug WHERE exp_dt='0000-00-00';