from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Producto, Cliente, Venta
from .forms import ProductoForm, ClienteForm, VentaForm

def lista_productos(request):
    #Muestra lista de productos activos en el sistema
    productos = Producto.objects.filter(activo=True)
    return render(request, 'inventario/lista_productos.html', {'productos': productos})

def agregar_producto(request):
    #Vista para crear nuevos productos
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto agregado correctamente.')
            return redirect('lista_productos')
    else:
        form = ProductoForm()
    return render(request, 'inventario/agregar_producto.html', {'form': form})

def editar_producto(request, pk):
    #Vista para modificar productos existentes
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado correctamente.')
            return redirect('lista_productos')
    else:
        form = ProductoForm(instance=producto)
    
    return render(request, 'inventario/editar_producto.html', {
        'form': form, 
        'producto': producto,
        'title': 'Editar Producto'
    })

def eliminar_producto(request, pk):
    #Eliminación lógica de productos (cambia estado activo a False)
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.activo = False  # Eliminación lógica en lugar de borrado físico
        producto.save()
        messages.success(request, 'Producto eliminado correctamente.')
        return redirect('lista_productos')
    return render(request, 'inventario/eliminar_producto.html', {'producto': producto})

def registrar_venta(request):
    #Vista principal para registrar nuevas ventas
    if request.method == 'POST':
        form = VentaForm(request.POST)
        if form.is_valid():
            producto = form.cleaned_data['producto']
            cantidad = form.cleaned_data['cantidad_vendida']
            rut_cliente = form.cleaned_data['rut_cliente']
            es_habitual = form.cleaned_data['es_cliente_habitual']

            # Validar stock disponible
            if cantidad > producto.cantidad:
                messages.error(request, 'Stock insuficiente para realizar la venta.')
                return redirect('registrar_venta')

            # Manejar cliente habitual vs ocasional
            cliente_nombre = None
            if es_habitual:
                try:
                    cliente = Cliente.objects.get(rut=rut_cliente)
                    cliente_nombre = cliente.nombre
                except Cliente.DoesNotExist:
                    # Redirigir a registro si cliente habitual no existe
                    return redirect('registrar_cliente_con_rut', rut=rut_cliente)

            # Crear venta y detalle de forma transaccional
            from .models import Venta, VentaDetalle
            from django.db import transaction

            try:
                with transaction.atomic():
                    venta = Venta.objects.create(
                        cliente_rut=rut_cliente,
                        cliente_nombre=cliente_nombre,
                    )
                    detalle = VentaDetalle.objects.create(
                        venta=venta,
                        producto=producto,
                        cantidad_vendida=cantidad,
                        precio_unitario=producto.precio,
                    )
                    # VentaDetalle.save() calcula subtotal
                    # Actualizar stock
                    producto.cantidad -= cantidad
                    producto.save()
                    # Calcular total y guardar
                    venta.calcular_total()
                    venta.save()
            except Exception as e:
                messages.error(request, f'Error al registrar la venta: {e}')
                return redirect('registrar_venta')

            messages.success(request, f'Venta registrada correctamente. Total: ${venta.total}')
            return redirect('lista_ventas')
    else:
        form = VentaForm()
    
    return render(request, 'inventario/registrar_venta.html', {'form': form})

def registrar_cliente_con_rut(request, rut):
    #Vista para completar registro de cliente habitual durante proceso de venta
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save(commit=False)
            cliente.rut = rut  # Usa el RUT pasado por URL
            cliente.es_habitual = True
            cliente.save()
            messages.success(request, 'Cliente registrado como habitual.')
            return redirect('registrar_venta')  # Vuelve al registro de venta
    else:
        form = ClienteForm(initial={'rut': rut})  # Pre-carga el RUT en el formulario
    
    return render(request, 'inventario/registrar_cliente.html', {'form': form})

def lista_ventas(request):
    #Muestra historial completo de todas las ventas
    ventas = Venta.objects.all()
    return render(request, 'inventario/lista_ventas.html', {'ventas': ventas})