INSERT INTO Students_answers(id_test,
                             id_student, 
                             id_question, 
                             manual_check) 
                         SELECT id_test, 
                             id_student, 
                             Questions.id_question,
                             Questions.manual_check
                         FROM temp_result_table,
                         Questions WHERE Questions.id_question = temp_result_table.id_question;

DROP TABLE temp_all_variant;
DROP TABLE temp_result_table;