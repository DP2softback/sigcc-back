from login.models import Employee, User
from login.serializers import EmployeeSerializerRead, EmployeeSerializerWrite, UserSerializerRead
from rest_framework import serializers

from capacitaciones.models import AsistenciaSesionXEmpleado, EmpleadoXCursoEmpresa, LearningPath, CursoGeneral, CursoGeneralXLearningPath, CursoUdemy, CursoEmpresa, \
    Sesion, SesionXReponsable, Tema, Categoria, ProveedorEmpresa, Habilidad, ProveedorUsuario

from django.utils import timezone

class LearningPathSerializer(serializers.ModelSerializer):

    class Meta:
        model = LearningPath
        fields = '__all__'

    def validate_nombre(self, value):
        if value == '':
            raise serializers.ValidationError('El nombre no puede ser valor vacío')
        return value

    def validate_descripcion(self, value):
        if self.validate_nombre(self.context['nombre']) == value:
            raise serializers.ValidationError('La descripcion no puede ser igual al nombre')
        return value


class CursoUdemySerializer(serializers.ModelSerializer):

    class Meta:
        model = CursoUdemy
        exclude = ('curso_x_learning_path',)

    def validate_udemy_id(self, value):

        if value == '':
            raise serializers.ValidationError('El valor de este campo no puede ser vacio')

        return value

class CursoEmpresaSerializer(serializers.ModelSerializer):
    sesiones= serializers.SerializerMethodField()
    class Meta:
        model = CursoEmpresa
        exclude = ('curso_x_learning_path',)
        #exclude = ('curso_x_learning_path','asistencia_x_empleado')
        
    def get_sesiones(self,obj):
        sesiones= Sesion.objects.filter(cursoEmpresa=obj)
        return SesionSerializer(sesiones,many=True).data

    def validate_tipo(self, value):

        if value == '':
            raise serializers.ValidationError('El valor de este campo no puede ser vacio')
        return value
    
    def validate_nombre(self, value):
        if value == '':
            raise serializers.ValidationError('El nombre no puede ser valor vacío')
        return value

    def validate_descripcion(self, value):
        if self.validate_nombre(self.context['nombre']) == value:
            raise serializers.ValidationError('La descripcion no puede ser igual al nombre')
        return value


class LearningPathSerializerWithCourses(serializers.ModelSerializer):

    curso_x_learning_path = serializers.SerializerMethodField()

    class Meta:
        model = LearningPath
        fields = '__all__'

    def get_curso_x_learning_path(self, obj):
        cursos_id = CursoGeneralXLearningPath.objects.filter(learning_path=obj).values_list('curso_id', flat=True)
        cursos = CursoUdemy.objects.filter(id__in=cursos_id)
        return CursoUdemySerializer(cursos, many=True).data


class SesionXReponsableSerializer(serializers.ModelSerializer):
    class Meta:
        model = SesionXReponsable
        fields = '__all__'



class SesionSerializer(serializers.ModelSerializer):
    temas= serializers.SerializerMethodField()
    responsables= serializers.SerializerMethodField()

    class Meta:
        model = Sesion
        exclude = ('sesion_x_responsable', 'cursoEmpresa',)
        #exclude = ('curso_x_learning_path','asistencia_x_empleado')

    def get_temas(self,obj):
        temas= Tema.objects.filter(sesion=obj)
        return TemaSerializer(temas,many=True).data

    def get_responsables(self,obj):
        responsables= ProveedorEmpresa.objects.filter(sesion=obj)
        return ProveedorEmpresaSerializer(responsables,many=True).data

    def validate_nombre(self, value):
        if value == '':
            raise serializers.ValidationError('El nombre no puede ser valor vacío')
        return value

    def validate_descripcion(self, value):
        if self.validate_nombre(self.context['nombre']) == value:
            raise serializers.ValidationError('La descripcion no puede ser igual al nombre')
        return value

class TemaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tema
        exclude = ('sesion',)
        #exclude = ('curso_x_learning_path','asistencia_x_empleado')
        
    def validate_nombre(self, value):
        if value == '':
            raise serializers.ValidationError('El nombre no puede ser valor vacío')
        return value
    
class ProveedorUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProveedorUsuario
        exclude = ('habilidad_x_proveedor_usuario',)
        #exclude = ('curso_x_learning_path','asistencia_x_empleado')

class AsistenciaSesionSerializer(serializers.ModelSerializer):
    empleado_nombre = serializers.CharField(source='empleado.user.first_name')
    empleado_datos = serializers.SerializerMethodField()
    
    class Meta:
        model = AsistenciaSesionXEmpleado
        fields = ['id', 'curso_empresa', 'empleado', 'empleado_nombre', 'empleado_datos', 'sesion', 'estado_asistencia'] 
    
    def get_empleado_datos(self, obj):
        empleado = obj.empleado
        empleado_serializer = EmployeeSerializerRead(empleado)
        return empleado_serializer.data
    
'''
class CursoEmpresaSerializerWithEmpleados(serializers.ModelSerializer):

    asistencia_x_empleado = serializers.SerializerMethodField()

    class Meta:
        model = Empleados
        fields = '__all__'

    def get_asistencia_x_empleado(self, obj):
        cursos_id = AsistenciaCursoEmpresaXEmpleado.objects.filter(curso_empresa=obj).values_list('empleado_id', flat=True)
        empleados = Empleado.objects.filter(id__in=empleado_id)
        return Empleadoserializer(empleados, many=True).data
'''


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'


class ProveedorEmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProveedorEmpresa
        fields = '__all__'


class HabilidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habilidad
        fields = '__all__'


class ProveedorUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProveedorUsuario
        fields = '__all__'


class CursoGeneralListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CursoGeneral
        fields = ['id', 'nombre', 'descripcion']

class CursoEmpresaListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CursoEmpresa
        fields = ['id', 'nombre', 'descripcion', 'es_libre']


class CursoSesionTemaResponsableListSerializer(serializers.ModelSerializer):
    sesiones = SesionSerializer(many=True)

    class Meta:
        model = CursoEmpresa
        fields = ['id', 'nombre', 'descripcion', 'sesiones']

class EmpleadoXCursoEmpresaForBossSerializer(serializers.ModelSerializer):
    employees = serializers.SerializerMethodField()

    class Meta:
        model = EmpleadoXCursoEmpresa
        fields = '__all__'

    def get_employees(self, obj):
        employees = obj.empleado_set.all()
        return EmployeeSerializerRead(employees, many=True).data

class CursoSesionTemaResponsableEmpleadoListSerializer(serializers.ModelSerializer):
    sesiones = serializers.SerializerMethodField()
    empleados = serializers.SerializerMethodField()

    class Meta:
        model = CursoEmpresa
        exclude = ('curso_empresa_x_empleado',)

    def get_sesiones(self,obj):
        sesiones= Sesion.objects.filter(cursoEmpresa=obj)
        return SesionSerializer(sesiones,many=True).data
    
    def get_empleados(self,obj):
        empleados = EmpleadoXCursoEmpresa.objects.filter(cursoEmpresa=obj)
        return EmpleadoXCursoEmpresaForBossSerializer(empleados, many=True, context=self.context).data


class BusquedaEmployeeSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(source='pk')
    email = serializers.EmailField(source='user.email')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')

    class Meta:
        model = Employee
        fields = ['id', 'email', 'first_name', 'last_name']


class CursosEmpresaSerialiazer(serializers.ModelSerializer):
    class Meta:
        model = CursoEmpresa
        fields = '__all__'

class EmpleadoXCursoEmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmpleadoXCursoEmpresa
        fields = '__all__'