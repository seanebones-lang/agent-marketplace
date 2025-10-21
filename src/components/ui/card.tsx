/**
 * Card Component
 */

import { FC, ReactNode } from 'react';
import { clsx } from 'clsx';

interface CardProps {
  children: ReactNode;
  className?: string;
  hover?: boolean;
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

export const Card: FC<CardProps> = ({
  children,
  className,
  hover = false,
  padding = 'md',
}) => {
  const paddingStyles = {
    none: '',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };

  return (
    <div
      className={clsx(
        'bg-gray-50 dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700',
        paddingStyles[padding],
        hover && 'transition-shadow hover:shadow-lg',
        className
      )}
    >
      {children}
    </div>
  );
};

export const CardHeader: FC<{ children: ReactNode; className?: string }> = ({
  children,
  className,
}) => (
  <div className={clsx('border-b border-gray-200 pb-4 mb-4', className)}>
    {children}
  </div>
);

export const CardTitle: FC<{ children: ReactNode; className?: string }> = ({
  children,
  className,
}) => (
  <h3 className={clsx('text-xl font-semibold text-gray-900', className)}>
    {children}
  </h3>
);

export const CardContent: FC<{ children: ReactNode; className?: string }> = ({
  children,
  className,
}) => <div className={clsx('text-gray-600', className)}>{children}</div>;

export const CardFooter: FC<{ children: ReactNode; className?: string }> = ({
  children,
  className,
}) => (
  <div className={clsx('border-t border-gray-200 pt-4 mt-4', className)}>
    {children}
  </div>
);

