import { AnimatePresence, motion } from "framer-motion";
import { ReactNode } from "react";

export const AnimatedWrapper = ({children}:{children:ReactNode}) => {
  return (
    <AnimatePresence>
      <motion.div
        key="search-component"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.4, ease: 'easeInOut' }}
        className="overflow-hidden"
      >
       {children}
      </motion.div>
    </AnimatePresence>
  )
}