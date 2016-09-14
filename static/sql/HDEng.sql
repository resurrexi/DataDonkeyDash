with ASO_GROUPS as
    (
        select distinct GP_NB
        from EDWPVW.EDW_ATUL_MBR_ENRT_HSTRY
        where DACL_ATUL_FNDG_CD not in ('F','N','U','M')
            and GP_ENRT_YRMO_NB = (select max(GP_ENRT_YRMO_NB) from EDWPVW.EDW_ATUL_MBR_ENRT_HSTRY where DACL_ACTV_IN = 'Y')
            and DACL_ACTV_IN = 'Y'
    )
select GROUP
    ,count(distinct CNSR_INDV_ID) as TOTAL_MEMBERS
    ,count(distinct(case when TOTAL_COACH_ATTEMPTS_CT > '0' then CNSR_INDV_ID end)) as MBR_ATTEMPTED
    ,count(distinct(case when DACL_RCHD_IN = '1' then CNSR_INDV_ID end)) as MBR_REACHED
    ,count(distinct(case when (COACH_MBR_DECISION_ACTIVITY_CT > '0'
            or COACH_PROVIDED_CMI_ACTIVITY_CT > '0'
            or MEMBER_PROVIDED_CMI_ACTIVITY_CT > '0')
        then CNSR_INDV_ID end)) as MBR_ENGAGED
from
    (
        select case{4}
                when GP_NB in (select GP_NB from ASO_GROUPS) then 'All Other ASO'
                else 'Other' end as GROUP
            ,CNSR_INDV_ID
            ,TOTAL_COACH_ATTEMPTS_CT
            ,DACL_RCHD_IN
            ,COACH_MBR_DECISION_ACTIVITY_CT
            ,COACH_PROVIDED_CMI_ACTIVITY_CT
            ,MEMBER_PROVIDED_CMI_ACTIVITY_CT
        from EDWPVW.EDW_HD_CNSR_CND
        where MDLX_RTGP_END_DT between {0} and {1}
            and (GP_NB in (select GP_NB from ASO_GROUPS)
                or GP_NB in ({2}))
            and CNSR_INDV_ID is not null
            and DACL_CRN_CND_IN = '1'{3}
    )
group by GROUP