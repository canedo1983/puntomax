from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.factory import Factory
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.list import TwoLineAvatarIconListItem, IconLeftWidget, ThreeLineAvatarIconListItem
import database

# Intentar importar la cámara. Si falla, avisamos por consola.
try:
    from kivy_garden.zbarcam import ZBarCam
    HAS_CAM = True
except Exception as e:
    print(f"Aviso: Cámara desactivada en PC debido a: {e}. Funcionará nativa en Android.")
    HAS_CAM = False

# Simulamos tamaño de celular para probar en PC
Window.size = (360, 640)

KV = '''
<DialogoApertura@MDBoxLayout>:
    orientation: 'vertical'
    spacing: "12dp"
    size_hint_y: None
    height: "80dp"
    MDTextField:
        id: txt_monto_apertura
        hint_text: "Monto inicial en caja ($)"
        input_filter: 'float'

<DialogoCierre@MDBoxLayout>:
    orientation: 'vertical'
    spacing: "12dp"
    size_hint_y: None
    height: "130dp"
    MDLabel:
        id: lbl_resumen_cierre
        text: "Calculando..."
        markup: True
    MDTextField:
        id: txt_efectivo_real
        hint_text: "Efectivo real contado ($)"
        input_filter: 'float'

<DialogoProducto@MDBoxLayout>:
    orientation: 'vertical'
    spacing: "12dp"
    size_hint_y: None
    height: "320dp"
    MDTextField:
        id: txt_codigo
        hint_text: "Código de Barras / SKU"
    MDTextField:
        id: txt_nombre
        hint_text: "Nombre del Producto"
    MDTextField:
        id: txt_precio
        hint_text: "Precio de Venta ($)"
        input_filter: 'float'
    MDTextField:
        id: txt_costo
        hint_text: "Costo ($)"
        input_filter: 'float'
    MDTextField:
        id: txt_stock
        hint_text: "Cantidad en Stock"
        input_filter: 'int'

<DialogoCliente@MDBoxLayout>:
    orientation: 'vertical'
    spacing: "12dp"
    size_hint_y: None
    height: "120dp"
    MDTextField:
        id: txt_nombre_cliente
        hint_text: "Nombre del Cliente"
    MDTextField:
        id: txt_telefono_cliente
        hint_text: "Teléfono"

<DialogoGasto@MDBoxLayout>:
    orientation: 'vertical'
    spacing: "12dp"
    size_hint_y: None
    height: "220dp"
    MDTextField:
        id: txt_monto_gasto
        hint_text: "Monto del Gasto ($)"
        input_filter: 'float'
    MDTextField:
        id: txt_desc_gasto
        hint_text: "Descripción (Ej: Luz, Proveedor)"
    MDLabel:
        text: "¿De dónde sale la plata?"
    MDBoxLayout:
        spacing: "10dp"
        MDRaisedButton:
            text: "Efectivo"
            on_release: app.set_metodo_gasto("Efectivo")
        MDRaisedButton:
            text: "Transferencia"
            md_bg_color: 0.2, 0.6, 0.2, 1
            on_release: app.set_metodo_gasto("Transferencia")
    MDLabel:
        id: lbl_metodo_gasto
        text: "Seleccionado: Efectivo"
        theme_text_color: "Hint"

<ContenidoCobro@MDBoxLayout>:
    orientation: 'vertical'
    spacing: "12dp"
    size_hint_y: None
    height: "250dp"
    MDLabel:
        id: lbl_total_pagar
        text: "Total: $0.00"
        font_style: "H5"
    MDLabel:
        text: "Método de Pago:"
    MDBoxLayout:
        spacing: "10dp"
        MDRaisedButton:
            text: "Efectivo"
            on_release: app.set_metodo_pago("Efectivo")
        MDRaisedButton:
            text: "Transferencia"
            md_bg_color: 0.2, 0.6, 0.2, 1
            on_release: app.set_metodo_pago("Transferencia")
    MDLabel:
        id: lbl_metodo_seleccionado
        text: "Seleccionado: Efectivo"
        theme_text_color: "Hint"
    MDTextField:
        id: txt_efectivo
        hint_text: "Paga con (sólo si es efectivo):"
        input_filter: 'float'
        on_text: app.calcular_vuelto(self.text)
    MDLabel:
        id: lbl_vuelto
        text: "Vuelto: $0.00"

MDNavigationLayout:
    MDScreenManager:
        id: screen_manager

        # --- DASHBOARD ---
        MDScreen:
            name: 'dashboard'
            MDBoxLayout:
                orientation: 'vertical'
                MDTopAppBar:
                    title: "Dashboard"
                    left_action_items: [["menu", lambda x: nav_drawer.set_state("open")]]
                MDBoxLayout:
                    orientation: 'vertical'
                    padding: "20dp"
                    spacing: "20dp"
                    MDCard:
                        padding: "16dp"
                        size_hint_y: None
                        height: "120dp"
                        md_bg_color: 0.9, 0.95, 1, 1
                        MDBoxLayout:
                            orientation: 'vertical'
                            MDLabel:
                                text: "ARQUEO DE CAJA (HOY)"
                                font_style: "Subtitle2"
                            MDLabel:
                                id: lbl_dash_efectivo
                                text: "Efectivo en Caja: $0.00"
                                font_style: "H6"
                            MDLabel:
                                id: lbl_dash_transf
                                text: "Transferencias: $0.00"
                                font_style: "H6"
                    MDBoxLayout:
                        spacing: "10dp"
                        size_hint_y: None
                        height: "50dp"
                        MDRaisedButton:
                            text: "ABRIR CAJA"
                            size_hint_x: 0.5
                            on_release: app.mostrar_dialogo_apertura()
                        MDRaisedButton:
                            text: "CERRAR CAJA"
                            size_hint_x: 0.5
                            md_bg_color: 0.8, 0.2, 0.2, 1
                            on_release: app.mostrar_dialogo_cierre()
                    MDWidget:

        # --- PRODUCTOS E INVENTARIO ---
        MDScreen:
            name: 'productos'
            MDBoxLayout:
                orientation: 'vertical'
                MDTopAppBar:
                    title: "Inventario / Productos"
                    left_action_items: [["menu", lambda x: nav_drawer.set_state("open")]]
                MDFloatLayout:
                    MDScrollView:
                        MDList:
                            id: lista_productos
                    MDFloatingActionButton:
                        icon: "plus"
                        pos_hint: {"center_x": .85, "center_y": .1}
                        on_release: app.mostrar_dialogo_producto()

        # --- GASTOS ---
        MDScreen:
            name: 'gastos'
            MDBoxLayout:
                orientation: 'vertical'
                MDTopAppBar:
                    title: "Registrar Gasto"
                    left_action_items: [["menu", lambda x: nav_drawer.set_state("open")]]
                MDFloatLayout:
                    MDLabel:
                        text: "Usá el botón + para registrar gastos, pago a proveedores, etc. Se descontará del arqueo."
                        halign: "center"
                        pos_hint: {"center_y": .6}
                        padding_x: "20dp"
                    MDFloatingActionButton:
                        icon: "plus"
                        pos_hint: {"center_x": .85, "center_y": .1}
                        on_release: app.mostrar_dialogo_gasto()

        # --- CLIENTES ---
        MDScreen:
            name: 'clientes'
            MDBoxLayout:
                orientation: 'vertical'
                MDTopAppBar:
                    title: "Mis Clientes"
                    left_action_items: [["menu", lambda x: nav_drawer.set_state("open")]]
                MDFloatLayout:
                    MDScrollView:
                        MDList:
                            id: lista_clientes
                    MDFloatingActionButton:
                        icon: "plus"
                        pos_hint: {"center_x": .85, "center_y": .1}
                        on_release: app.mostrar_dialogo_cliente()

        # --- VENTAS ---
        MDScreen:
            name: 'ventas'
            MDBoxLayout:
                orientation: 'vertical'
                MDTopAppBar:
                    title: "Punto de Venta"
                    left_action_items: [["menu", lambda x: nav_drawer.set_state("open")]]
                MDBoxLayout:
                    orientation: 'vertical'
                    padding: "8dp"
                    spacing: "5dp"
                    
                    # Selección de Cliente
                    MDRaisedButton:
                        id: btn_cliente
                        text: "Cliente: Consumidor Final (Tocar para cambiar)"
                        size_hint_x: 1
                        md_bg_color: 0.5, 0.5, 0.5, 1
                        on_release: app.seleccionar_cliente()
                    
                    MDBoxLayout:
                        size_hint_y: None
                        height: "50dp"
                        spacing: "5dp"
                        MDTextField:
                            id: input_escaner
                            hint_text: "Escribir Código (Enter)"
                            on_text_validate: app.escanear_codigo(self.text)
                        MDIconButton:
                            icon: "barcode-scan"
                            on_release: app.abrir_camara()
                    
                    MDScrollView:
                        size_hint_y: 0.4
                        MDList:
                            id: lista_carrito
                    MDBoxLayout:
                        size_hint_y: None
                        height: "50dp"
                        MDLabel:
                            id: lbl_total_general
                            text: "Total: $0.00"
                            font_style: "H6"
                        MDRaisedButton:
                            text: "COBRAR"
                            on_release: app.mostrar_dialogo_cobro()

        # --- CÁMARA ESCÁNER ---
        MDScreen:
            name: 'camara'
            MDBoxLayout:
                orientation: 'vertical'
                MDTopAppBar:
                    title: "Escaneando..."
                    left_action_items: [["arrow-left", lambda x: app.cambiar_pantalla('ventas')]]
                MDBoxLayout:
                    id: contenedor_camara
                    MDLabel:
                        text: "Cámara nativa lista para Android."
                        halign: "center"

    # --- MENU LATERAL ---
    MDNavigationDrawer:
        id: nav_drawer
        MDBoxLayout:
            orientation: 'vertical'
            padding: "8dp"
            spacing: "2dp"
            MDLabel:
                text: "Punto-MAX ERP"
                font_style: "H5"
                size_hint_y: None
                height: self.texture_size[1]
            ScrollView:
                MDList:
                    OneLineIconListItem:
                        text: "Dashboard / Arqueo"
                        on_release: app.cambiar_pantalla('dashboard')
                        IconLeftWidget:
                            icon: "view-dashboard"
                    OneLineIconListItem:
                        text: "Ventas"
                        on_release: app.cambiar_pantalla('ventas')
                        IconLeftWidget:
                            icon: "cart"
                    OneLineIconListItem:
                        text: "Productos / Inventario"
                        on_release: app.cambiar_pantalla('productos')
                        IconLeftWidget:
                            icon: "package-variant"
                    OneLineIconListItem:
                        text: "Clientes"
                        on_release: app.cambiar_pantalla('clientes')
                        IconLeftWidget:
                            icon: "account-group"
                    OneLineIconListItem:
                        text: "Gastos y Egresos"
                        on_release: app.cambiar_pantalla('gastos')
                        IconLeftWidget:
                            icon: "cash-minus"
'''

class PuntoMaxApp(MDApp):
    carrito = []
    total_venta = 0.0
    metodo_pago_actual = "Efectivo"
    metodo_gasto_actual = "Efectivo"
    cliente_actual_id = 1
    
    dialog_apertura = None
    dialog_cierre = None
    dialog_cobro = None
    dialog_cliente = None
    dialog_gasto = None
    dialog_selec_cliente = None
    dialog_producto = None

    def build(self):
        self.theme_cls.primary_palette = "Blue"
        database.crear_tablas()
        return Builder.load_string(KV)

    def on_start(self):
        self.actualizar_dashboard()
        self.cargar_clientes()
        self.cargar_productos()
        self.configurar_camara()

    def cambiar_pantalla(self, nombre):
        self.root.ids.screen_manager.current = nombre
        self.root.ids.nav_drawer.set_state("close")
        if nombre == 'dashboard':
            self.actualizar_dashboard()

    # --- DASHBOARD Y APERTURA/CIERRE DE CAJA ---
    def actualizar_dashboard(self):
        efvo, transf = database.arqueo_caja()
        self.root.ids.lbl_dash_efectivo.text = f"Efectivo en Caja: ${efvo:.2f}"
        self.root.ids.lbl_dash_transf.text = f"Transferencias: ${transf:.2f}"

    def mostrar_dialogo_apertura(self):
        if not self.dialog_apertura:
            self.dialog_apertura = MDDialog(
                title="Abrir Caja", type="custom", content_cls=Factory.DialogoApertura(),
                buttons=[
                    MDFlatButton(text="CANCELAR", on_release=lambda x: self.dialog_apertura.dismiss()),
                    MDFlatButton(text="ABRIR", on_release=self.guardar_apertura),
                ])
        self.dialog_apertura.open()

    def guardar_apertura(self, *args):
        c = self.dialog_apertura.content_cls
        try:
            monto = float(c.ids.txt_monto_apertura.text) if c.ids.txt_monto_apertura.text else 0.0
            database.registrar_movimiento_caja('Apertura', 'Efectivo', monto, "Apertura diaria")
            self.actualizar_dashboard()
            self.dialog_apertura.dismiss()
            c.ids.txt_monto_apertura.text = ""
        except ValueError:
            pass

    def mostrar_dialogo_cierre(self):
        efvo, transf = database.arqueo_caja()
        if not self.dialog_cierre:
            self.dialog_cierre = MDDialog(
                title="Cierre de Caja", type="custom", content_cls=Factory.DialogoCierre(),
                buttons=[
                    MDFlatButton(text="CANCELAR", on_release=lambda x: self.dialog_cierre.dismiss()),
                    MDFlatButton(text="CERRAR CAJA", theme_text_color="Custom", text_color=(0.8, 0.2, 0.2, 1), on_release=self.guardar_cierre),
                ])
        # Actualizamos el texto con lo que hay en caja
        self.dialog_cierre.content_cls.ids.lbl_resumen_cierre.text = f"Esperado en caja: [b]${efvo:.2f}[/b]\nTransferencias: [b]${transf:.2f}[/b]"
        self.dialog_cierre.open()

    def guardar_cierre(self, *args):
        c = self.dialog_cierre.content_cls
        efvo_esperado, transf = database.arqueo_caja()
        try:
            texto = c.ids.txt_efectivo_real.text
            efvo_real = float(texto) if texto != "" else efvo_esperado
            diferencia = efvo_real - efvo_esperado
            desc = f"Cierre de caja. Diferencia: ${diferencia:.2f}"
            
            # Guarda en la base de datos que se cerró la caja
            database.registrar_movimiento_caja('Cierre', 'Efectivo', efvo_real, desc)
            
            self.dialog_cierre.dismiss()
            c.ids.txt_efectivo_real.text = ""
            
            # Se reinician los valores mostrados al usuario
            self.actualizar_dashboard()
        except ValueError:
            pass

    # --- PRODUCTOS E INVENTARIO ---
    def mostrar_dialogo_producto(self):
        if not self.dialog_producto:
            self.dialog_producto = MDDialog(
                title="Nuevo Producto", type="custom", content_cls=Factory.DialogoProducto(),
                buttons=[
                    MDFlatButton(text="CANCELAR", on_release=lambda x: self.dialog_producto.dismiss()),
                    MDFlatButton(text="GUARDAR", on_release=self.guardar_producto),
                ])
        self.dialog_producto.open()

    def guardar_producto(self, *args):
        c = self.dialog_producto.content_cls
        codigo = c.ids.txt_codigo.text
        nombre = c.ids.txt_nombre.text
        try:
            precio = float(c.ids.txt_precio.text)
            costo = float(c.ids.txt_costo.text) if c.ids.txt_costo.text else 0.0
            stock = int(c.ids.txt_stock.text)
            
            if codigo and nombre:
                guardado = database.agregar_producto(codigo, nombre, precio, costo, stock)
                if guardado:
                    self.cargar_productos()
                    self.dialog_producto.dismiss()
                    c.ids.txt_codigo.text = ""
                    c.ids.txt_nombre.text = ""
                    c.ids.txt_precio.text = ""
                    c.ids.txt_costo.text = ""
                    c.ids.txt_stock.text = ""
        except ValueError:
            pass

    def cargar_productos(self):
        lista = self.root.ids.lista_productos
        lista.clear_widgets()
        for prod in database.obtener_productos():
            item = ThreeLineAvatarIconListItem(
                text=f"{prod[1]} (Cód: {prod[0]})", 
                secondary_text=f"Precio: ${prod[2]:.2f} - Costo: ${prod[4]:.2f}",
                tertiary_text=f"Stock disponible: {prod[3]}"
            )
            item.add_widget(IconLeftWidget(icon="package-variant"))
            lista.add_widget(item)

    # --- GASTOS ---
    def mostrar_dialogo_gasto(self):
        self.metodo_gasto_actual = "Efectivo"
        if not self.dialog_gasto:
            self.dialog_gasto = MDDialog(
                title="Nuevo Gasto", type="custom", content_cls=Factory.DialogoGasto(),
                buttons=[
                    MDFlatButton(text="CANCELAR", on_release=lambda x: self.dialog_gasto.dismiss()),
                    MDFlatButton(text="REGISTRAR", on_release=self.guardar_gasto),
                ])
        self.dialog_gasto.open()

    def set_metodo_gasto(self, metodo):
        self.metodo_gasto_actual = metodo
        if self.dialog_gasto:
            self.dialog_gasto.content_cls.ids.lbl_metodo_gasto.text = f"Seleccionado: {metodo}"

    def guardar_gasto(self, *args):
        c = self.dialog_gasto.content_cls
        desc = c.ids.txt_desc_gasto.text
        try:
            monto = float(c.ids.txt_monto_gasto.text)
            database.registrar_movimiento_caja('Egreso', self.metodo_gasto_actual, monto, desc)
            self.dialog_gasto.dismiss()
            self.actualizar_dashboard()
            c.ids.txt_monto_gasto.text = ""
            c.ids.txt_desc_gasto.text = ""
        except ValueError:
            pass

    # --- CLIENTES ---
    def mostrar_dialogo_cliente(self):
        if not self.dialog_cliente:
            self.dialog_cliente = MDDialog(
                title="Nuevo Cliente", type="custom", content_cls=Factory.DialogoCliente(),
                buttons=[
                    MDFlatButton(text="CANCELAR", on_release=lambda x: self.dialog_cliente.dismiss()),
                    MDFlatButton(text="GUARDAR", on_release=self.guardar_cliente),
                ])
        self.dialog_cliente.open()

    def guardar_cliente(self, *args):
        c = self.dialog_cliente.content_cls
        nombre = c.ids.txt_nombre_cliente.text
        telefono = c.ids.txt_telefono_cliente.text
        if nombre:
            database.agregar_cliente(nombre, telefono)
            self.cargar_clientes()
            self.dialog_cliente.dismiss()

    def cargar_clientes(self):
        lista = self.root.ids.lista_clientes
        lista.clear_widgets()
        for cli in database.obtener_clientes():
            item = TwoLineAvatarIconListItem(text=cli[1], secondary_text=f"Tel: {cli[2]}")
            item.add_widget(IconLeftWidget(icon="account"))
            lista.add_widget(item)

    def seleccionar_cliente(self):
        items = []
        for cli in database.obtener_clientes():
            items.append(TwoLineAvatarIconListItem(
                text=cli[1], 
                on_release=lambda x, c_id=cli[0], c_nom=cli[1]: self.set_cliente_venta(c_id, c_nom)
            ))
            
        self.dialog_selec_cliente = MDDialog(title="Seleccionar Cliente", type="simple", items=items)
        self.dialog_selec_cliente.open()

    def set_cliente_venta(self, c_id, c_nom):
        self.cliente_actual_id = c_id
        self.root.ids.btn_cliente.text = f"Cliente: {c_nom} (Tocar para cambiar)"
        self.dialog_selec_cliente.dismiss()

    # --- CAMARA ---
    def configurar_camara(self):
        if HAS_CAM:
            contenedor = self.root.ids.contenedor_camara
            contenedor.clear_widgets()
            self.zbarcam = ZBarCam()
            self.zbarcam.bind(symbols=self.on_barcode_scanned)
            contenedor.add_widget(self.zbarcam)

    def abrir_camara(self):
        if HAS_CAM:
            self.cambiar_pantalla('camara')
        else:
            self.root.ids.input_escaner.text = "Cámara desactivada en PC"

    def on_barcode_scanned(self, instance, symbols):
        if not symbols: return
        codigo_leido = symbols[0].data.decode('utf-8')
        self.escanear_codigo(codigo_leido)
        self.cambiar_pantalla('ventas')

    # --- VENTAS ---
    def escanear_codigo(self, codigo_escaneado):
        if not codigo_escaneado: return
        for prod in database.obtener_productos():
            if prod[0] == codigo_escaneado:
                self.agregar_al_carrito(prod)
                break
        self.root.ids.input_escaner.text = ""
        self.root.ids.input_escaner.focus = True

    def agregar_al_carrito(self, producto):
        codigo, nombre, precio, stock, costo = producto
        for item in self.carrito:
            if item['codigo'] == codigo:
                item['cantidad'] += 1
                self.actualizar_carrito_ui()
                return
        self.carrito.append({'codigo': codigo, 'nombre': nombre, 'precio': precio, 'cantidad': 1})
        self.actualizar_carrito_ui()

    def actualizar_carrito_ui(self):
        lista = self.root.ids.lista_carrito
        lista.clear_widgets()
        self.total_venta = 0.0
        for item in self.carrito:
            subtotal = item['precio'] * item['cantidad']
            self.total_venta += subtotal
            li = ThreeLineAvatarIconListItem(text=f"{item['nombre']} (x{item['cantidad']})", secondary_text=f"Subtotal: ${subtotal:.2f}")
            li.add_widget(IconLeftWidget(icon="cart"))
            lista.add_widget(li)
        self.root.ids.lbl_total_general.text = f"Total: ${self.total_venta:.2f}"

    def mostrar_dialogo_cobro(self):
        if not self.carrito: return
        self.metodo_pago_actual = "Efectivo"
        content = Factory.ContenidoCobro()
        content.ids.lbl_total_pagar.text = f"Total a pagar: ${self.total_venta:.2f}"
        
        self.dialog_cobro = MDDialog(
            title="Cobrar Venta", type="custom", content_cls=content,
            buttons=[
                MDFlatButton(text="CANCELAR", on_release=lambda x: self.dialog_cobro.dismiss()),
                MDFlatButton(text="CONFIRMAR", on_release=lambda x: self.finalizar_venta(content)),
            ])
        self.dialog_cobro.open()

    def set_metodo_pago(self, metodo):
        self.metodo_pago_actual = metodo
        if self.dialog_cobro:
            self.dialog_cobro.content_cls.ids.lbl_metodo_seleccionado.text = f"Seleccionado: {metodo}"

    def calcular_vuelto(self, txt):
        try:
            efectivo = float(txt) if txt else 0.0
            vuelto = efectivo - self.total_venta
            self.dialog_cobro.content_cls.ids.lbl_vuelto.text = f"Vuelto: ${vuelto:.2f}"
        except ValueError: pass

    def finalizar_venta(self, content):
        database.registrar_venta(self.carrito, self.total_venta, self.metodo_pago_actual, self.cliente_actual_id)
        self.carrito = []
        self.actualizar_carrito_ui()
        self.actualizar_dashboard()
        self.cargar_productos()  # Actualiza stock en pantalla de inventario
        self.dialog_cobro.dismiss()

if __name__ == '__main__':
    PuntoMaxApp().run()