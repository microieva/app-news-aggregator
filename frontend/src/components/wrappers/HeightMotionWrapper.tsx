import { AnimatePresence, motion } from "framer-motion";
import { ReactNode } from "react";

export const HeightMotionWrapper = ({children}:{children:ReactNode}) => {
  return (
    <AnimatePresence>
      <motion.div
        key="height-motion"
        initial={{ opacity: 0, height: 0 }}
        animate={{ opacity: 1, height:'auto' }}
        exit={{ opacity: 0, height: 0 }}
        transition={{ duration: 0.5, ease: 'easeInOut' }}
        className="overflow-hidden"
      >
       {children}
      </motion.div>
    </AnimatePresence>
  )
}