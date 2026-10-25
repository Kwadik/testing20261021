"use client";

import { useEffect } from "react";

export function TelegramInitializer() {
    useEffect(() => {
        const webApp = window.Telegram?.WebApp;

        if (!webApp) return;

        const root = document.documentElement;

        const applyTheme = () => {
            const theme = webApp.themeParams;

            if (theme.bg_color)
                root.style.setProperty("--color-bg", theme.bg_color);

            if (theme.text_color)
                root.style.setProperty("--color-text", theme.text_color);

            if (theme.button_color)
                root.style.setProperty("--color-primary", theme.button_color);

            if (theme.secondary_bg_color)
                root.style.setProperty("--color-surface", theme.secondary_bg_color);

            root.style.setProperty(
                "--tg-viewport-height",
                `${webApp.viewportHeight}px`,
            );

            root.style.setProperty(
                "--tg-viewport-stable-height",
                `${webApp.viewportStableHeight}px`,
            );

            if (theme.bg_color) {
                webApp.setHeaderColor?.(theme.bg_color);
            }
        };

        webApp.ready();
        webApp.expand();

        applyTheme();

        webApp.onEvent?.("themeChanged", applyTheme);
        webApp.onEvent?.("viewportChanged", applyTheme);

        return () => {
            webApp.offEvent?.("themeChanged", applyTheme);
            webApp.offEvent?.("viewportChanged", applyTheme);
        };
    }, []);

    return null;
}