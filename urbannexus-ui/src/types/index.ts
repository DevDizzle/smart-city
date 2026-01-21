export interface Zone {
  zone_id: string;
  name: string;
  description: string;
  attributes: Record<string, any>;
  coordinates: [number, number][]; // Simple polygon
}

export interface Goal {
  type: string;
  description: string;
  priority: string;
  enabled?: boolean;
}

export interface Constraint {
  type: string;
  description: string;
}
