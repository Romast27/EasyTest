import sys
import project_Authorize
import project_Teacher
import project_Student

from PyQt5.QtWidgets import QApplication


if __name__ == '__main__':
    app = QApplication(sys.argv)
    #authorizing = project_Authorize.Authorize()
    #authorizing.show()
    #if not authorizing.exec_() and authorizing.authorized == 'teacher':
    if input() == '1':
        #window_teacher = project_Teacher.MainWindowTeacher(authorizing.name)
        window_teacher = project_Teacher.MainWindowTeacher('ФИ Учителя')
        window_teacher.show()
        #authorizing.close()
    #elif authorizing.authorized == 'student':
    else:
        #window_student = project_Student.MainWindowStudent(authorizing.name, authorizing.id)
        window_student = project_Student.MainWindowStudent('Ученик', 2)
        window_student.show()
        #authorizing.close()
    sys.exit(app.exec_())
