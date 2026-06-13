import csv

# Define the 100 headers
headers = [
    "Mapping_ID","Project_Name","Subject_Area","Phase_Release","Sprint_ID","Business_Owner","Technical_Lead","Data_Architect","STTM_Version","STTM_Status",
    "Approval_Date","Approved_By","Change_Request_ID","Source_System_ID","Source_System_Name","Source_Connection_Type","Source_Database","Source_Schema","Source_Table_View","Source_Table_Physical_Name",
    "Source_Table_Type","Source_Column_ID","Source_Column_Name","Source_Column_Physical_Name","Source_Data_Type","Source_Length","Source_Precision","Source_Scale","Source_Is_Nullable","Source_Is_PK",
    "Source_Is_FK","Source_FK_Reference_Table","Source_Default_Value","Source_Character_Set","Source_Collation","Source_Description","Source_Security_Classification","Is_PII_Source","Extraction_Type","Extraction_SQL_Override",
    "Delta_Capture_Mechanism","Incremental_Column","Source_Volume_Estimate","Source_Update_Frequency","Business_Rule_ID","Business_Rule_Name","Business_Rule_Description","Transformation_Type","Transformation_Logic","Lookup_Table_Name",
    "Lookup_Join_Condition","Lookup_Return_Column","Fallback_Value","Aggregation_Type","Filter_Condition","Data_Quality_Rule_ID","Data_Quality_Rule_Description","Null_Handling_Policy","Data_Type_Coercion_Rule","Pre_Truncate_Target",
    "Target_System_ID","Target_System_Name","Target_Connection_Type","Target_Database","Target_Schema","Target_Table_Physical_Name","Target_Table_Logical_Name","Target_Table_Type","Target_Column_ID","Target_Column_Name",
    "Target_Column_Physical_Name","Target_Data_Type","Target_Length","Target_Precision","Target_Scale","Target_Is_Nullable","Target_Is_PK","Target_Is_FK","Target_FK_Reference_Table","Target_Default_Value",
    "Target_Distribution_Style","Target_Sort_Cluster_Key","Is_PII_Target","Target_Security_Classification","Data_Masking_Rule","Encryption_Algorithm","SCD_Type","SCD_Effective_Date_Column","SCD_End_Date_Column","SCD_Current_Flag_Column",
    "Surrogate_Key_Generation_Mechanism","Is_Audit_Column","Audit_Created_By_Column","Audit_Created_Date_Column","Audit_Updated_By_Column","Audit_Updated_Date_Column","Mapping_Owner","QA_Status","Deployment_Package_ID","Notes_Comments"
]

subjects = ["Finance", "Customer Experience", "Supply Chain", "Human Resources", "Marketing"]
systems = [("SRC_01", "Oracle_ERP", "FIN_PROD"), ("SRC_02", "Salesforce_CRM", "SF_CLOUD"), ("SRC_03", "SAP_SCM", "LOGISTICS"), ("SRC_04", "Workday_HR", "HR_PROD"), ("SRC_05", "Adobe_Marketo", "MKT_ANALYTICS")]

with open('sttm_stress_test_1000.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file, quoting=csv.QUOTE_ALL)
    writer.writerow(headers)
    
    for i in range(1, 1001):
        idx = i % 5
        subj = subjects[idx]
        sys_id, sys_name, sys_db = systems[idx]
        
        row = [
            f"M_{i:04d}", "Enterprise Data Platform", subj, "Phase 2.1", f"Sprint_{10 + (i % 10)}", "Sarah Jenkins", "Amit Singh", "David Vance", "2.4", "Approved",
            "2026-05-12", "Sarah Jenkins", f"CR-2026-{1000+i}", sys_id, sys_name, "JDBC" if idx%2==0 else "API_REST", sys_db, "CORE_OWNER", f"TBL_SRC_{i}", f"SRC_PHYS_{i}",
            "Base Table", str(i), f"Col_Name_{i}", f"COL_PHYS_{i}", "NUMBER" if idx%2==0 else "VARCHAR2", "18" if idx%2==0 else "255", "18" if idx%2==0 else "0", "2" if idx%2==0 else "0", "N" if i%3==0 else "Y", "Y" if i%10==1 else "N",
            "N", "REF_TABLE_XYZ", "0.00", "AL32UTF8", "BINARY", f"Source column description metadata index {i}", "Restricted" if i%4==0 else "Internal", "Y" if i%7==0 else "N", "Incremental", f"SELECT * FROM TBL_SRC_{i} WHERE UPDATE_DT > :MIN_DATE",
            "CDC", "UPDATE_DT", "50000000", "Daily", f"BR_{i:03d}", "Data Normalization", f"Ensure parsing checks pass for business domain criteria on item {i}.", "Complex Lookup", f"CASE WHEN SRC.COL_PHYS_{i} IS NULL THEN 'N/A' ELSE UPPER(SRC.COL_PHYS_{i}) END", "LKP_VAL_TABLE",
            "SRC.KEY = LKP.KEY", "LKP_VAL", "UNKNOWN", "NONE", "WHERE STATUS_FLAG = 'A'", f"DQ_{i:03d}", "Validate formatting constraints and structures.", "Reject Row", "Explicit Cast", "N",
            "TGT_01", "Snowflake_DW", "Snowflake_Storage", "ANALYTICS_DB", f"CORE_{subj.upper()[:4]}", f"FACT_TGT_{i}", f"Target Logical Line {i}", "Fact", str(i), f"Tgt_Col_{i}",
            f"TGT_COL_{i}", "NUMBER" if idx%2==0 else "VARCHAR", "18" if idx%2==0 else "255", "18" if idx%2==0 else "0", "2" if idx%2==0 else "0", "Y", "N", "N", "", "0.00",
            "KEY(ID)", "AUTO", "Y" if i%7==0 else "N", "Internal", "None" if i%7!=0 else "MASK_SHA256", "None", "SCD1", "N/A", "N/A", "N/A",
            "N/A", "N", "DW_LOAD_PROCESS", "DW_LOAD_DATE", "DW_UPDATE_PROCESS", "DW_UPDATE_DATE", "Data_Eng_Team", "Passed", f"PKG_2026_V{i%5}", f"Stress dataset row simulation {i} of 1000."
        ]
        writer.writerow(row)

print("Generated sttm_stress_test_1000.csv with 100 columns and 1000 rows successfully.")