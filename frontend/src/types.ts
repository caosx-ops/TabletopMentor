// TabletopMentor 类型定义

export interface RuleCard {
  rule_id: string;
  game: string;
  version: string;
  section: string;
  rule_text: string;
  keywords: string[];
  complexity: "basic" | "intermediate" | "advanced";
  source_language: string;
  translations?: Record<string, string>;
  related_rules: string[];
  common_mistakes: string[];
  examples: string[];
  source_url?: string;
  updated_at?: string;
}

export interface Judgement {
  judgement_id: string;
  user_id: string;
  game: string;
  scenario: string;
  ruling: string;
  confidence: number;
  related_rules: string[];
  approved: boolean;
  status?: "pending" | "approved" | "rejected" | "saved";
  notes?: string;
  created_at: string;
}

export interface GamingPreference {
  id: string;
  user_id: string;
  preference_type: "positive" | "negative";
  content: string;
  games: string[];
  created_at: string;
}

// 保留原有类型以保持兼容性
export interface ProductCard {
  product_id: string;
  title: string;
  brand: string;
  category: string;
  description: string;
  skus: Array<{
    sku_id: string;
    spec: string;
    price_major: number;
    currency: string;
    stock: number;
  }>;
  default_sku_id?: string;
  image_url?: string;
  image_alt?: string;
  rating_summary?: {
    average: number;
    review_count: number;
  };
  landed_price?: {
    total_major: number;
    currency: string;
    breakdown: {
      subtotal_major: number;
      shipping_major: number;
      tax_major: number;
    };
  };
}
