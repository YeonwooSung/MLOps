create database if not exists temp;

/** 1) 기본 피처 생성 */
drop table if exists temp.ineligible_loan_model_features_01;
create table temp.ineligible_loan_model_features_01 as
select a.applicant_id
      ,a.cust_id
      ,b.gender
      ,b.married
      ,b.education
      ,b.self_employed
      ,a.applicant_income
      ,a.coapplicant_income
      ,a.loan_amount_term
      ,a.credit_history
      ,a.property_area
  from mlops.loan_applicant_info a left outer join
       mlops.cust_info           b on (    a.applicant_date = b.base_dt
                                       and a.cust_id = b.cust_id)
 where a.applicant_date between CONCAT(DATE_FORMAT(DATE_ADD(STR_TO_DATE('{{ ds_nodash }}', '%Y%m%d'), INTERVAL -6 MONTH), '%Y%m'), '01')
                            and DATE_FORMAT(LAST_DAY(DATE_ADD(STR_TO_DATE('{{ ds_nodash }}', '%Y%m%d'), INTERVAL -1 MONTH)), '%Y%m%d')
;

/** 2) 가족관련 피처 생성 */
drop table if exists temp.ineligible_loan_model_features_02;
create table temp.ineligible_loan_model_features_02 as
select c.cust_id
      ,c.family_dependents
  from (select a.cust_id
              ,case when count(1) >= 3
                    then '3+'
                    else cast(count(1) as char)
                end as family_dependents
          from mlops.loan_applicant_info a inner join
               mlops.family_info         b on (    a.applicant_date = b.base_dt
                                               and a.cust_id = b.cust_id)
         where a.applicant_date between CONCAT(DATE_FORMAT(DATE_ADD(STR_TO_DATE('{{ ds_nodash }}', '%Y%m%d'), INTERVAL -6 MONTH), '%Y%m'), '01')
                                    and DATE_FORMAT(LAST_DAY(DATE_ADD(STR_TO_DATE('{{ ds_nodash }}', '%Y%m%d'), INTERVAL -1 MONTH)), '%Y%m%d')
         group by a.cust_id
       ) c
;

/** 3) 피처 합치기 */
drop table if exists temp.ineligible_loan_model_features;
create table temp.ineligible_loan_model_features as
select a.applicant_id
      ,a.gender
      ,a.married
      ,b.family_dependents
      ,a.education
      ,a.self_employed
      ,a.applicant_income
      ,a.coapplicant_income
      ,a.loan_amount_term
      ,a.credit_history
      ,a.property_area
  from temp.ineligible_loan_model_features_01 a left outer join
       temp.ineligible_loan_model_features_02 b on (a.cust_id = b.cust_id)
;

/** 4) 타겟 (답안지) 생성 */
drop table if exists temp.ineligible_loan_model_target;
create table temp.ineligible_loan_model_target as
select a.applicant_id
      ,case when b.loan_account_id is not null and b.registration_date between a.applicant_date
                                                                           and DATE_FORMAT(DATE_ADD(STR_TO_DATE(a.applicant_date, '%Y%m%d'), INTERVAL 89 DAY), '%Y%m%d') /*90일*/
            then 'Loan Default'
            else 'Creditworthy'
        end as loan_status
  from mlops.loan_applicant_info a left outer join
       (select b.loan_account_id
              ,b.registration_date
          from mlops.loan_default_account b
       ) b on (b.loan_account_id = a.loan_account_id)
 where a.applicant_date between CONCAT(DATE_FORMAT(DATE_ADD(STR_TO_DATE('{{ ds_nodash }}', '%Y%m%d'), INTERVAL -6 MONTH), '%Y%m'), '01') and DATE_FORMAT(LAST_DAY(DATE_ADD(STR_TO_DATE('{{ ds_nodash }}', '%Y%m%d'), INTERVAL -1 MONTH)), '%Y%m%d')
;

/** 5) 피처와 타겟 합치기 (모델 학습 최종 데이터)  */
delete
  from mlops.ineligible_loan_model_features_target
  where base_ym = DATE_FORMAT(DATE_ADD(STR_TO_DATE('{{ ds_nodash }}', '%Y%m%d'
                                                  ), INTERVAL -1 MONTH
                                      ), '%Y%m'
                             );
insert
  into mlops.ineligible_loan_model_features_target
      (base_ym
      ,applicant_id
      ,gender
      ,married
      ,family_dependents
      ,education
      ,self_employed
      ,applicant_income
      ,coapplicant_income
      ,loan_amount_term
      ,credit_history
      ,property_area
      ,loan_status
      )
select DATE_FORMAT(DATE_ADD(STR_TO_DATE('{{ ds_nodash }}', '%Y%m%d'
                                       ), INTERVAL -1 MONTH
                           ), '%Y%m'
                  ) as base_ym
      ,a.applicant_id
      ,a.gender
      ,a.married
      ,a.family_dependents
      ,a.education
      ,a.self_employed
      ,a.applicant_income
      ,a.coapplicant_income
      ,a.loan_amount_term
      ,a.credit_history
      ,a.property_area
      ,b.loan_status
  from temp.ineligible_loan_model_features a left outer join
       temp.ineligible_loan_model_target   b on (a.applicant_id = b.applicant_id)
;
