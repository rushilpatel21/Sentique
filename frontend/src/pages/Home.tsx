import { TrendingUp } from "lucide-react";
import  ButtonGroup  from "../components/ui/ButtonGroup";

export function Home() {
  return (
    <div>
      
      {/* ButtonGroup component without any operations */}
      <ButtonGroup defaultSelected="DEFAULT" onSelectionChange={() => {}} />
    </div>
  );
}
