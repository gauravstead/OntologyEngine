import { create } from 'zustand';

interface Entity {
    uid: string;
    name: string;
    type: string;
    riskScore: number;
}

interface GraphState {
    activeEntities: Entity[];
    selectedEntity: Entity | null;
    systemStatus: string;
    setActiveEntities: (entities: Entity[]) => void;
    setSelectedEntity: (entity: Entity | null) => void;
    setSystemStatus: (status: string) => void;
}

export const useStore = create<GraphState>((set) => ({
    activeEntities: [],
    selectedEntity: null,
    systemStatus: 'INITIALIZING',
    setActiveEntities: (entities) => set({ activeEntities: entities }),
    setSelectedEntity: (entity) => set({ selectedEntity: entity }),
    setSystemStatus: (status) => set({ systemStatus: status }),
}));
