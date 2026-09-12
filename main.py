import os
import shutil
import qrcode
import flet as ft
from playwright.async_api import async_playwright

def generar_codigo_qr(url: str, ruta_salida_qr: str):
    """Genera una imagen PNG del código QR basado en la URL facilitada."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(ruta_salida_qr)

async def generar_exportacion(url: str, formato: str, ruta_guardado: str):
    """Abre la URL introducida en Playwright y genera el PDF o PNG."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(
            viewport={"width": 1200, "height": 1600},
            device_scale_factor=2
        )
        
        await page.goto(url, wait_until="networkidle")
        
        if formato == "pdf":
            await page.pdf(
                path=ruta_guardado,
                format="A4",
                print_background=True,
                margin={"top": "0px", "right": "0px", "bottom": "0px", "left": "0px"}
            )
        elif formato == "png":
            await page.screenshot(
                path=ruta_guardado,
                full_page=True
            )
            
        await browser.close()

async def main(page: ft.Page):
    page.title = "Generador de CV y Código QR"
    page.window.width = 520
    page.window.height = 740
    page.window.resizable = False
    page.padding = 25
    page.theme_mode = ft.ThemeMode.LIGHT

    lbl_titulo = ft.Text("Generador de CV + QR", size=22, weight=ft.FontWeight.BOLD)
    
    txt_url = ft.TextField(
        label="URL dinámica de la web o CV",
        hint_text="https://tuweb.com/mi-cv",
        border_radius=8
    )
    
    dd_formato = ft.Dropdown(
        label="Formato de exportación del CV",
        options=[
            ft.dropdown.Option("pdf", "PDF"),
            ft.dropdown.Option("png", "Imagen (PNG)"),
        ],
        value="pdf",
        border_radius=8
    )

    lbl_estado = ft.Text("", size=14)
    btn_generar = ft.ElevatedButton("Generar QR y Exportar CV", height=45)
    
    # Campo para escribir el nombre personalizado del archivo QR
    txt_nombre_qr = ft.TextField(
        label="Nombre del archivo QR",
        hint_text="ej: mi_cv_qr",
        value="codigo_qr",
        border_radius=8,
        visible=False,
        width=300
    )
    
    # Botón para descargar de forma independiente el QR
    btn_guardar_qr = ft.OutlinedButton("Guardar código QR (PNG)", visible=False, height=40)
    
    img_qr_preview = ft.Image(
        src="",
        width=150,
        height=150,
        fit="contain",
        visible=False
    )

    # Ruta temporal local
    ruta_qr_temp = os.path.abspath("qr_generado_temp.png")

    async def procesar_exportacion(e):
        url = txt_url.value.strip()
        if not url:
            lbl_estado.value = "Introduce una URL válida."
            lbl_estado.color = "red"
            page.update()
            return

        formato = dd_formato.value
        ext = "pdf" if formato == "pdf" else "png"
        ruta_salida = os.path.abspath(f"curriculum_exportado.{ext}")

        lbl_estado.value = "Generando código QR y procesando web..."
        lbl_estado.color = "blue"
        btn_generar.disabled = True
        page.update()

        try:
            # 1. Generar la imagen del código QR dinámico
            generar_codigo_qr(url, ruta_qr_temp)
            
            # Mostrar la vista previa y activar las opciones de guardado del QR
            img_qr_preview.src = ruta_qr_temp
            img_qr_preview.visible = True
            txt_nombre_qr.visible = True
            btn_guardar_qr.visible = True
            page.update()

            # 2. Renderizar y exportar la web a través de Playwright
            await generar_exportacion(url, formato, ruta_salida)
            
            lbl_estado.value = f"¡Éxito! CV exportado en:\n{ruta_salida}"
            lbl_estado.color = "green"
        except Exception as err:
            lbl_estado.value = f"Error: {str(err)}"
            lbl_estado.color = "red"
        finally:
            btn_generar.disabled = False
            page.update()

    # Función para guardar el QR con el nombre personalizado elegible
    async def descargar_qr_personalizado(e):
        if os.path.exists(ruta_qr_temp):
            nombre_limpio = txt_nombre_qr.value.strip() or "codigo_qr"
            if not nombre_limpio.endswith(".png"):
                nombre_limpio += ".png"
                
            destino = os.path.abspath(nombre_limpio)
            shutil.copy(ruta_qr_temp, destino)
            
            lbl_estado.value = f"¡QR guardado correctamente como:\n{destino}"
            lbl_estado.color = "green"
            page.update()

    btn_generar.on_click = procesar_exportacion
    btn_guardar_qr.on_click = descargar_qr_personalizado

    page.add(
        ft.Column(
            controls=[
                lbl_titulo,
                txt_url,
                dd_formato,
                btn_generar,
                ft.Row([img_qr_preview], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([txt_nombre_qr], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([btn_guardar_qr], alignment=ft.MainAxisAlignment.CENTER),
                lbl_estado
            ],
            spacing=15,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )

# ✅ SINTAXIS MODERNA (Flet 0.80+)
if __name__ == "__main__":
    ft.run(main)