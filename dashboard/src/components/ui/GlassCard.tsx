import { ReactNode } from 'react';
import { motion } from 'framer-motion';

interface GlassCardProps {
  title?: string;
  children: ReactNode;
  className?: string;
  headerRight?: ReactNode;
}

export const GlassCard = ({ title, children, className = '', headerRight }: GlassCardProps) => (
  <motion.div
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.3 }}
    className={`
      bg-white/5 backdrop-blur-xl rounded-2xl
      border border-white/10 shadow-2xl
      overflow-hidden flex flex-col
      ${className}
    `}
  >
    {title && (
      <div className="px-4 py-3 border-b border-white/10 flex items-center justify-between shrink-0">
        <h3 className="text-white/80 font-medium text-sm">{title}</h3>
        {headerRight}
      </div>
    )}
    <div className="flex-1 overflow-hidden">
      {children}
    </div>
  </motion.div>
);
