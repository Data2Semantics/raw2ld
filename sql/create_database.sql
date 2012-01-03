delimiter $$

CREATE DATABASE `aers` /*!40100 DEFAULT CHARACTER SET latin1 */$$

delimiter $$

CREATE TABLE `demo` (
  `isr` int(11) NOT NULL,
  `case` int(11) DEFAULT NULL,
  `i_f_cod` varchar(45) DEFAULT NULL,
  `foll_seq` varchar(45) DEFAULT NULL,
  `image` varchar(45) DEFAULT NULL,
  `event_dt` date DEFAULT NULL,
  `mfr_dt` date DEFAULT NULL,
  `fda_dt` date DEFAULT NULL,
  `rept_cod` varchar(45) DEFAULT NULL,
  `mfr_num` varchar(45) DEFAULT NULL,
  `mfr_sndr` varchar(45) DEFAULT NULL,
  `age` varchar(45) DEFAULT NULL,
  `age_cod` varchar(45) DEFAULT NULL,
  `gndr_cod` varchar(45) DEFAULT NULL,
  `e_sub` varchar(45) DEFAULT NULL,
  `wt` varchar(45) DEFAULT NULL,
  `wt_cod` varchar(45) DEFAULT NULL,
  `rept_dt` date DEFAULT NULL,
  `occp_cod` varchar(45) DEFAULT NULL,
  `death_dt` date DEFAULT NULL,
  `to_mfr` varchar(45) DEFAULT NULL,
  `confid` varchar(45) DEFAULT NULL,
  `reporter_country` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`isr`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1$$

delimiter $$

CREATE TABLE `drug` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `isr` int(11) NOT NULL,
  `drug_seq` varchar(45) NOT NULL,
  `role_cod` varchar(45) DEFAULT NULL,
  `drugname` varchar(45) DEFAULT NULL,
  `val_vbm` varchar(45) DEFAULT NULL,
  `route` varchar(45) DEFAULT NULL,
  `dose_vbm` varchar(45) DEFAULT NULL,
  `dechal` varchar(45) DEFAULT NULL,
  `rechal` varchar(45) DEFAULT NULL,
  `lot_num` varchar(45) DEFAULT NULL,
  `exp_dt` date DEFAULT NULL,
  `nda_num` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `NAME` (`drugname`),
  KEY `ISR` (`isr`),
  KEY `drug_seq` (`drug_seq`),
  KEY `isrseqname` (`isr`,`drug_seq`,`drugname`)
) ENGINE=InnoDB AUTO_INCREMENT=687034 DEFAULT CHARSET=latin1$$

delimiter $$

CREATE TABLE `outc` (
  `isr` int(11) DEFAULT NULL,
  `outc_cod` varchar(45) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1$$

delimiter $$

CREATE TABLE `reac` (
  `isr` int(11) DEFAULT NULL,
  `pt` varchar(45) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1$$

delimiter $$

CREATE TABLE `ther` (
  `isr` int(11) DEFAULT NULL,
  `drug_seq` varchar(45) DEFAULT NULL,
  `start_dt` date DEFAULT NULL,
  `end_dt` date DEFAULT NULL,
  `dur` varchar(45) DEFAULT NULL,
  `dur_cod` varchar(45) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1$$


