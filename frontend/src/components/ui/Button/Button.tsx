import type { ButtonHTMLAttributes } from "react";
import styles from "./Button.module.scss";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
    variant?: "primary" | "secondary" | "ghost";
    active?: boolean;
};

export function Button({
                           variant = "primary",
                           active = false,
                           className,
                           type = "button",
                           ...props
                       }: ButtonProps) {
    return (
        <button
            type={type}
            className={[
                styles.button,
                styles[variant],
                active ? styles.active : "",
                className ?? "",
            ]
                .filter(Boolean)
                .join(" ")}
            {...props}
        />
    );
}