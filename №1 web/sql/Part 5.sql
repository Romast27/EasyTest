SELECT DISTINCT Test_for_student.id_test, CASE WHEN type_work = 1 THEN ('Тест по теме «' || theme || '»') WHEN type_work = 2 THEN ('Контрольная работа №' || num_work) END, CASE WHEN id_student THEN (SELECT name_student FROM Students WHERE Test_for_student.id_student = Students.id_student) END, CASE WHEN mark IS NULL THEN ('нет') ELSE (mark || ' баллов') END FROM Test_for_student LEFT JOIN Tests ON Test_for_student.id_test = Tests.id_test LEFT JOIN Test_info ON Test_for_student.id_test = Test_info.id_test