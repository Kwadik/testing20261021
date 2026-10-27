interface Window {
    Telegram?: {
        WebApp?: {
            ready(): void;
            expand(): void;

            viewportHeight: number;
            viewportStableHeight: number;

            colorScheme: "light" | "dark";

            themeParams: {
                bg_color?: string;
                text_color?: string;
                button_color?: string;
                button_text_color?: string;
                secondary_bg_color?: string;
            };

            initDataUnsafe?: {
                user?: {
                    first_name?: string;
                    last_name?: string;
                    username?: string;
                };
            };

            setHeaderColor?(color: string): void;

            onEvent?(
                event: "themeChanged" | "viewportChanged",
                callback: () => void,
            ): void;

            offEvent?(
                event: "themeChanged" | "viewportChanged",
                callback: () => void,
            ): void;
        };
    };
}