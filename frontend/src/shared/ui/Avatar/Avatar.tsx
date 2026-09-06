import type { JSX } from 'react';
import { cn } from '../../lib/cn';
import styles from './Avatar.module.css';
import type { AvatarProps } from './Avatar.props';

export const Avatar = ({ firstName, lastName, size=48, variant='circle', className, style, ...props }: AvatarProps): JSX.Element => {
    
    const getInitials = () => {
        if (!firstName && !lastName) return ''; 
        const firstLetter = firstName ? firstName.charAt(0) : '';
        const lastLetter = lastName ? lastName.charAt(0) : '';
        return `${firstLetter}${lastLetter}`.toUpperCase();
    };
    
    const dynamicStyle = {
        width: size,
        height: size,
        fontSize: Math.round(size * 0.4),
        ...style
    };

    return (
        <div 
            className={cn(
                styles.avatar, 
                styles[variant], 
                className
            )}
            style={dynamicStyle}
            {...props}
        >
            <span>{getInitials()}</span>
        </div>
    );
};