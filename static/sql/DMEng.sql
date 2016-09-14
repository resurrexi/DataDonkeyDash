select to_number(cvg.EXT_CVG_ID) as MEMBER_ID
    ,1 as MBR_IDENTIFIED
    ,max(case when asmt.ENC_IDN is not null and invn.ENC_IDN is not null then 1 else 0 end) as MBR_ENGAGED
from JIVA.MV_MODEL_EPISODES ep
inner join JIVA.V_MODEL_EPISODE_COVERAGE cvg
on ep.ENC_IDN = cvg.ENC_IDN
    and cvg.ACTIVE = 'Y'
left join
    (select distinct ENC_IDN
    from JIVA.V_MODEL_EPISODE_ASSESSMENTS
    where ACE_TYPE = 'Initial Assessment'
        and TITLE not in ('FB Mbr Sat Survey','FEP Cost Benefit Analysis','FEP OPL','FEP Short Term Interventions'
            ,'Non Program Engagement Intervention Check list','Preventive screening')
        and ACTIVE='Y') asmt
on ep.ENC_IDN = asmt.ENC_IDN
left join
    (select distinct ENC_IDN
    from JIVA.V_MODEL_INTERVENTIONS
    where INTERVENTION_STATUS = 'Closed'
        and ACTIVE = 'Y') invn
on ep.ENC_IDN = invn.ENC_IDN
where ep.EPISODE_TYPE_CD = 'DM'
    and EPISODE_START_DATE >= add_months(sysdate,-12)
    and cvg.EXT_CVG_ID is not null
    and ep.ACTIVE = 'Y'
group by cvg.EXT_CVG_ID