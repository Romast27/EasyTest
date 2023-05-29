SELECT
    CASE WHEN type_work = 1 THEN ('Тест по теме «' || theme || '»')
        WHEN type_work = 2 THEN ('Контрольная работа №' || num_work) END,
    CASE WHEN starting_date IS NULL THEN ('Без ограничения по времени')
        ELSE ('Начало - ' || starting_date || '    Конец - ' || ending_date) END 
FROM Tests 
LEFT JOIN Test_info ON Tests.id_test = Test_info.id_test 
WHERE Tests.id_test={0}