import { create } from 'zustand'
import { devtools } from 'zustand/middleware'

type UiState = {
  activeContactId: string
  setActiveContactId: (id: string) => void
  sidebarOpen: boolean
  toggleSidebar: () => void
}

export const useUiStore = create<UiState>()(
  devtools(
    (set) => ({
      activeContactId: 'c1',
      setActiveContactId: (id) => set({ activeContactId: id }),
      sidebarOpen: true,
      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
    }),
    {
      name: 'qrypta-ui-store',
    },
  ),
)
