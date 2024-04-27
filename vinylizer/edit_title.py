from tkinter import Button, StringVar, Tk, Text

def edit_title(message: str):
    def check_input():
        if len(text_box.get("1.0", "end-1c")) <= 60:
            new_message.set(text_box.get("1.0", "end-1c"))
            ws.destroy()
        else:
            create_warning(ws)
    
    def update_text_length(event):
        text_length.delete('1.0', 'end')
        text_length.insert('end', f'{str(len(text_box.get("1.0", "end-1c")))}/60')
        if len(text_box.get("1.0", "end-1c")) > 60:
            text_length.config(bg='white')
        else:
            text_length.config(bg='green')

    def create_main_window():
        ws = Tk()
        ws.geometry('600x100')
        ws.config(bg='#fcbc99')
        ws.title('Editar título')
        return ws

    def create_text_length(ws):
        text_length = Text(
            ws,
            height=1,
            width=5
        )

        text_length.insert('end', f'{str(len(text_box.get("1.0", "end-1c")))}/60')
        text_length.pack(expand=True)
        return text_length

    def create_text_box(ws):
        text_box = Text(
            ws,
            height=12,
            width=60
        )
        text_box.pack(expand=True)
        text_box.insert('end', message)
        text_box.bind("<Key>", update_text_length)
        return text_box
    

    def create_check_button(ws):
        check_button = Button(
            ws, 
            text = "Enviar",  
            command = check_input
            )

        check_button.pack()
        return check_button

    def create_warning(ws):
        warning = Text(
            ws,
            height=2,
            width=50,
            bg='white',
            fg='black',
            wrap='word'
        )
        warning.pack(expand=True)
        warning.insert('end', 'O título não pode ter mais de 60 caracteres. Por favor, modifique o texto.')
        ws.after(3000, warning.destroy)
        return warning

    ws = create_main_window()
    text_box = create_text_box(ws)
    text_length = create_text_length(ws)
    create_check_button(ws)
    new_message = StringVar()
    
    check_input()
    update_text_length('')
    ws.mainloop()

    return new_message.get()

if __name__ == '__main__':
    print(edit_title('a' * 61))
