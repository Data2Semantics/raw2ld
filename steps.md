<style>
	h1,h2,h3,h4,h5 {
		font-family: "Graublau Web", Helvetica, Arial, sans-serif;
		font-weight: normal;
		text-rendering: optimizeLegibility;
	}

	p, li {
		font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
  		font-size: 13px;
  		font-weight: normal;
  		line-height: 18px;
		text-rendering: optimizeLegibility;
	}
</style>


# Procedure for converting and linking AERS legacy data


## 1. Obtain source files

The Adverse Events Reporting System dumps its contents on a quarterly basis to zipfiles in both ASCII (dollar separated) and SGML format. These data files can be obtained from:

	<http://www.fda.gov/Drugs/GuidanceComplianceRegulatoryInformation/Surveillance/AdverseDrugEffects/ucm082193.htm>

The page lists direct links to the four most recent quarters:

* **AERS_ASCII_2011q2.ZIP** which is in fact a link to:  
	<http://www.fda.gov/downloads/Drugs/GuidanceComplianceRegulatoryInformation/Surveillance/AdverseDrugEffects/UCM278762.zip>
* **AERS_ASCII_2011q1.ZIP** which is in fact a link to:  
	<http://www.fda.gov/downloads/Drugs/GuidanceComplianceRegulatoryInformation/Surveillance/AdverseDrugEffects/UCM270803.zip>
* and so on

Older data sources can be obtained from:

	<http://www.fda.gov/Drugs/GuidanceComplianceRegulatoryInformation/Surveillance/AdverseDrugEffects/ucm083765.htm>

Which contains a similar list for quarterly dumps older than one year.



