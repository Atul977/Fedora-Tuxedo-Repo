use gtk::gdk::RGBA;
use gtk::gdk_pixbuf::Pixbuf;
use gtk::prelude::{
    ButtonExt, Cast, ColorChooserExt, GtkWindowExt, ObjectExt,
    WidgetExt, PopoverExt, NativeExt,
};
use relm4::{gtk, Component, ComponentParts, ComponentSender, RelmWidgetExt};
use tailor_api::Color;

use crate::state::{TailorStateMsg, STATE};
use crate::util;

pub struct ColorButton {
    pub color: Color,
    pixbuf: Pixbuf,
    popover: gtk::Popover,
}

#[derive(Debug)]
pub enum ColorButtonInput {
    ShowPicker,
    UpdateColor(Color),
}

#[relm4::component(pub)]
impl Component for ColorButton {
    type CommandOutput = ();
    type Init = Color;
    type Input = ColorButtonInput;
    type Output = Color;

    view! {
        #[root]
        gtk::Button {
            add_css_class: "color",
            set_width_request: 52,
            connect_clicked => ColorButtonInput::ShowPicker,

            #[name = "image"]
            gtk::Picture::for_pixbuf(&model.pixbuf) {
                inline_css: "border-radius: 2px",
                #[watch]
                set_pixbuf: Some(&model.pixbuf)
            }
        }
    }

    fn init(
        color: Self::Init,
        root: Self::Root,
        sender: ComponentSender<Self>,
    ) -> ComponentParts<Self> {
        let pixbuf = util::new_pixbuf(&color);

        // 1. Create the Popover (The mini-window)
        let popover = gtk::Popover::builder()
            .autohide(true)
            .build();
        
        // Manually attach parent
        popover.set_parent(&root);

        // 2. Create the Color Wheel Widget
        let color_widget = gtk::ColorChooserWidget::builder()
            .use_alpha(false)
            .build();
        
        // Manually format the hex string
        let hex_string = format!("#{:02x}{:02x}{:02x}", color.r, color.g, color.b);
        let initial_rgba = RGBA::parse(&hex_string).unwrap_or(RGBA::BLACK);
        color_widget.set_rgba(&initial_rgba);

        // 3. Connect the signal (Cloning sender first)
        let sender_clone = sender.clone();
        
        color_widget.connect_rgba_notify(move |c| {
            let rgba = c.rgba();
            let new_color = util::rgba_to_color(rgba);
            
            // Update the global app state immediately
            STATE.emit(TailorStateMsg::OverwriteColor(new_color.clone()));
            
            // Update the button icon using the clone
            sender_clone.input(ColorButtonInput::UpdateColor(new_color));
        });

        // Put the wheel inside the popover
        popover.set_child(Some(&color_widget));

        let model = Self { 
            pixbuf, 
            color, 
            popover 
        };

        let widgets = view_output!();

        ComponentParts { model, widgets }
    }

    fn update(&mut self, message: Self::Input, sender: ComponentSender<Self>, _root: &Self::Root) {
        match message {
            ColorButtonInput::ShowPicker => {
                // Show the color wheel popup
                self.popover.popup();
            }
            ColorButtonInput::UpdateColor(color) => {
                util::fill_pixbuf(&self.pixbuf, &color);
                self.color = color.clone();
                sender.output(color).ok();
            }
        }
    }
}
