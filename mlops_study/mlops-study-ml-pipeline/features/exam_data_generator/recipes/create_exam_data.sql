/** 1. recipe 테이블 데이터 생성
  */

/** recipe.recipe_target_applicants */
delete a
  from recipe.recipe_target_applicants a
 where a.base_dt = '{{ params.base_day }}'
;

insert
  into recipe.recipe_target_applicants
      (base_dt
      ,applicant_id
      ,loan_account_id)
select '{{ params.base_day }}' as base_dt
      ,a.applicant_id
      ,a.loan_account_id
  from mlops.loan_applicant_info a
 where a.applicant_date between '20230601' and '20231130'
   and rand({{ params.base_day }}) < 0.005
;

/** recipe.recipe_target_applicants_new_id */
delete a
  from recipe.recipe_target_applicants_new_id a
 where a.base_dt = '{{ params.base_day }}'
;

insert
  into recipe.recipe_target_applicants_new_id
      (base_dt
      ,applicant_id
      ,new_applicant_id
      ,loan_account_id
      ,new_loan_account_id)
select a.base_dt
      ,a.applicant_id
      ,concat(substr('{{ params.base_day }}', 3), lpad(cast(a.idx as char(4)), 4, '0')) as new_applicant_id
      ,a.loan_account_id
      ,concat('{{ params.base_day }}', lpad(cast(a.idx as char(4)), 4, '0')) as new_loan_account_id
  from (select a.base_dt
              ,a.applicant_id
              ,a.loan_account_id
              ,row_number() over (order by a.applicant_id desc) as idx
          from recipe.recipe_target_applicants a
         where a.base_dt = '{{ params.base_day }}'
       ) a
;

/** 2. recipe 테이블 데이터 생성
  */

/** mlops.cust_info */
delete a
  from mlops.cust_info a
 where a.base_dt = '{{ params.base_day }}'
;

insert
  into mlops.cust_info
      (base_dt
      ,cust_id
      ,gender
      ,married
      ,education
      ,self_employed)
select '{{ params.base_day }}' as base_dt
      ,a.cust_id
      ,a.gender
      ,a.married
      ,a.education
      ,a.self_employed
  from mlops.cust_info a
 where a.base_dt = '20231130'
;

/** mlops.family_info */
delete a
  from mlops.family_info a
 where a.base_dt = '{{ params.base_day }}'
;

insert
  into mlops.family_info
      (base_dt
      ,cust_id
      ,family_cust_id
      ,living_together
      )
select '{{ params.base_day }}' as base_dt
      ,a.cust_id
      ,a.family_cust_id
      ,a.living_together
  from mlops.family_info a
 where a.base_dt = '20231130'
;


/** mlops.loan_applicant_info */
delete a
  from mlops.loan_applicant_info a
 where a.applicant_id like concat(substr('{{ params.base_day }}', 3), '%')
;

insert
  into mlops.loan_applicant_info
      (applicant_id
      ,applicant_date
      ,applicant_time
      ,cust_id
      ,applicant_income
      ,coapplicant_income
      ,credit_history
      ,property_area
      ,loan_amount
      ,loan_amount_term
      ,loan_account_id
      )
select a.new_applicant_id as applicant_id
      ,'{{ params.base_day }}' as applicant_date
      ,b.applicant_time
      ,b.cust_id
      ,b.applicant_income
      ,b.coapplicant_income
      ,b.credit_history
      ,b.property_area
      ,b.loan_amount
      ,b.loan_amount_term
      ,a.new_loan_account_id as loan_account_id
  from recipe.recipe_target_applicants_new_id a inner join
       mlops.loan_applicant_info b on (a.applicant_id = b.applicant_id)
 where a.base_dt = '{{ params.base_day }}'
;


/** mlops.loan_default_account */
delete a
  from mlops.loan_default_account a
 where a.loan_account_id like concat('{{ params.base_day }}', '%')
;

insert
  into mlops.loan_default_account
      (loan_account_id
      ,registration_date
      ,registration_time
      ,loan_default
      )
select c.new_loan_account_id as loan_account_id
      ,date_format(date_add(str_to_date('{{ params.base_day }}', '%Y%m%d'), INTERVAL c.plus_days DAY), '%Y%m%d') as registration_date
      ,c.registration_time
      ,c.loan_default
  from (select a.new_loan_account_id
              ,abs(datediff(str_to_date('{{ params.base_day }}', '%Y%m%d'), str_to_date(b.registration_date, '%Y%m%d'))) % 89
                  as plus_days
              ,b.registration_time
              ,b.loan_default
          from recipe.recipe_target_applicants_new_id a inner join
               mlops.loan_default_account b on (a.loan_account_id = b.loan_account_id)
         where a.base_dt = '{{ params.base_day }}'
       ) c
;


/** 3. recipe 테이블 데이터 삭제
  */

/** recipe.recipe_target_applicants */
delete a
  from recipe.recipe_target_applicants a
 where a.base_dt = '{{ params.base_day }}'
;

/** recipe.recipe_target_applicants_new_id */
delete a
  from recipe.recipe_target_applicants_new_id a
 where a.base_dt = '{{ params.base_day }}'
;
