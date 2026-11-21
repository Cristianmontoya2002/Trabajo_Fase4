from typing import Any  # Permite recibir distintos tipos de datos.
from modelos import (  # Importa las clases y herramientas de la primera parte.
    Cliente, Servicio, Reserva, ReservaSala, AlquilerEquipo, Asesoria,
    ErrorSistema, ValidacionError, DuplicadoError, NoEncontradoError,
    EstadoReserva, formato_dinero, logger, LOG_FILE
)

# Reúne las operaciones principales del sistema.
class SistemaFJ:
    """Fachada de gestión en memoria: listas de objetos, sin persistencia de negocio."""
    def __init__(self):
        self.clientes: list[Cliente] = []  # Almacena los clientes registrados.
        self.servicios: list[Servicio] = []  # Almacena los servicios creados.
        self.reservas: list[Reserva] = []  # Almacena las reservas realizadas.

    # Crea un cliente y evita que se repita su correo electrónico.
    def registrar_cliente(self, nombre: str, correo: str, telefono: str) -> Cliente:
        cliente = Cliente(nombre, correo, telefono)
        if any(c.correo == cliente.correo for c in self.clientes):
            raise DuplicadoError(f"Ya existe el cliente con correo {cliente.correo}.")
        self.clientes.append(cliente)
        logger.info("Cliente registrado: %s", cliente.describir())
        return cliente

    # Agrega un servicio válido y evita nombres repetidos.
    def agregar_servicio(self, servicio: Servicio) -> Servicio:
        if not isinstance(servicio, Servicio):
            raise ValidacionError("El objeto debe ser una instancia de Servicio.")
        if any(s.nombre.casefold() == servicio.nombre.casefold() for s in self.servicios):
            raise DuplicadoError(f"Ya existe un servicio llamado '{servicio.nombre}'.")
        self.servicios.append(servicio)
        logger.info("Servicio agregado: %s", servicio.describir())
        return servicio

    # Busca un cliente por su identificador.
    def buscar_cliente(self, cliente_id: str) -> Cliente:
        for cliente in self.clientes:
            if cliente.id == cliente_id:
                return cliente
        raise NoEncontradoError(f"No existe el cliente {cliente_id}.")

    # Crea una reserva después de comprobar que existan el cliente y el servicio.
    def crear_reserva(self, cliente_id: str, servicio_id: str, duracion: Any) -> Reserva:
        cliente = self.buscar_cliente(cliente_id)
        servicio = next((s for s in self.servicios if s.id == servicio_id), None)
        if servicio is None:
            raise NoEncontradoError(f"No existe el servicio {servicio_id}.")
        reserva = Reserva(cliente, servicio, duracion)
        self.reservas.append(reserva)
        logger.info("Reserva %s creada", reserva.id)
        return reserva

# Ejecuta los casos de prueba y demostración que estaban en el código original.
def ejecutar_demo() -> None:
    """Demuestra más de 10 operaciones y mantiene la ejecución ante errores."""
    sistema = SistemaFJ()
    operaciones = 0

    # Ejecuta una acción individual y controla sus posibles errores.
    def ejecutar(etiqueta: str, accion):
        nonlocal operaciones
        operaciones += 1
        print(f"\\n{operaciones}. {etiqueta}")
        try:
            resultado = accion()
        except ErrorSistema as exc:
            logger.exception("Operación '%s' fallida: %s", etiqueta, exc)
            print(f"  Error controlado: {exc}")
        except Exception as exc:
            logger.exception("Error inesperado en '%s'", etiqueta)
            print(f"  Error inesperado registrado; el sistema continúa: {exc}")
        else:
            logger.info("Operación '%s' completada", etiqueta)
            if resultado is not None:
                print(f"  {resultado}")
        finally:
            print("  Operación finalizada.")

    clientes: dict[str, Cliente] = {}
    servicios: dict[str, Servicio] = {}
    reservas: dict[str, Reserva] = {}

    # Registra un cliente válido para las operaciones posteriores.
    def cliente_valido():
        c = sistema.registrar_cliente("Ana Pérez", "ana@example.com", "+57 3001234567")
        clientes["ana"] = c
        return c.describir()

    ejecutar("Registrar cliente válido", cliente_valido)
    ejecutar("Rechazar correo inválido", lambda: sistema.registrar_cliente("Luis", "correo-invalido", "3001234567"))
    ejecutar("Rechazar nombre vacío", lambda: sistema.registrar_cliente(" ", "x@example.com", "3001234567"))

    # Crea el servicio de reserva de sala.
    def crear_sala():
        s = sistema.agregar_servicio(ReservaSala("Sala Andina", 35000, 12))
        servicios["sala"] = s
        return s.describir()

    ejecutar("Crear servicio de sala", crear_sala)

    # Crea el servicio de alquiler de equipo.
    def crear_equipo():
        s = sistema.agregar_servicio(AlquilerEquipo("Proyector", 80000, 1))
        servicios["equipo"] = s
        return s.describir()

    ejecutar("Crear servicio de alquiler de equipo", crear_equipo)

    # Crea el servicio de asesoría.
    def crear_asesoria():
        s = sistema.agregar_servicio(Asesoria("Consultoría Python", 95000, "Desarrollo de software"))
        servicios["asesoria"] = s
        return s.describir()

    ejecutar("Crear servicio de asesoría", crear_asesoria)
    ejecutar("Rechazar tarifa cero", lambda: ReservaSala("Sala inválida", 0, 10))
    ejecutar("Rechazar creación de servicio con objeto incorrecto", lambda: sistema.agregar_servicio("No es Servicio"))

    # Crea una reserva válida de sala.
    def reserva_sala():
        r = sistema.crear_reserva(clientes["ana"].id, servicios["sala"].id, 2)
        reservas["sala"] = r
        return r.describir()

    ejecutar("Crear reserva válida de sala", reserva_sala)
    ejecutar("Confirmar reserva de sala", lambda: (reservas["sala"].confirmar(), reservas["sala"].describir())[1])
    ejecutar("Procesar reserva con impuesto y descuento", lambda: formato_dinero(reservas["sala"].procesar(impuesto="0.19", descuento="0.10")))
    ejecutar("Rechazar cancelación de reserva procesada", lambda: reservas["sala"].cancelar())
    ejecutar("Rechazar reserva con servicio inexistente", lambda: sistema.crear_reserva(clientes["ana"].id, "NO-EXISTE", 1))

    # Crea una reserva de equipo.
    def reserva_equipo():
        r = sistema.crear_reserva(clientes["ana"].id, servicios["equipo"].id, 2)
        reservas["equipo"] = r
        return r.describir()

    ejecutar("Crear reserva de equipo", reserva_equipo)
    ejecutar("Confirmar reserva de equipo", lambda: (reservas["equipo"].confirmar(), reservas["equipo"].describir())[1])
    ejecutar("Procesar reserva de equipo con variante de impuesto", lambda: formato_dinero(reservas["equipo"].servicio.calcular_costo_con_impuesto(2, "0.19")))
    ejecutar("Crear reserva con duración inválida", lambda: sistema.crear_reserva(clientes["ana"].id, servicios["asesoria"].id, -3))

    try:
        # Busca un cliente inexistente para demostrar el control de excepciones.
        sistema.buscar_cliente("CLIENTE-INEXISTENTE")
    except NoEncontradoError as exc:
        logger.exception("Búsqueda fallida en demostración")
        print(f"\\nBúsqueda controlada: {exc}")
    else:
        print("\\nCliente encontrado.")

    print(f"\\nDemostración terminada: {operaciones} operaciones; {len(sistema.clientes)} cliente(s), "
          f"{len(sistema.servicios)} servicio(s), {len(sistema.reservas)} reserva(s).")
    print(f"Eventos y errores registrados en: {LOG_FILE}")