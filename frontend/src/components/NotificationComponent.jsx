import React from "react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { CheckCircle, AlertCircle, Info, X } from "lucide-react";

const NotificationComponent = ({ notifications, onRemove }) => {
  if (!notifications || notifications.length === 0) return null;

  const getIcon = (type) => {
    switch (type) {
      case "success":
        return <CheckCircle className="h-4 w-4" />;
      case "error":
        return <AlertCircle className="h-4 w-4" />;
      default:
        return <Info className="h-4 w-4" />;
    }
  };

  const getVariant = (type) => {
    switch (type) {
      case "error":
        return "destructive";
      default:
        return "default";
    }
  };

  const getColorClasses = (type) => {
    switch (type) {
      case "success":
        return "border-green-500 bg-green-50 text-green-800";
      case "error":
        return "border-red-500 bg-red-50 text-red-800";
      default:
        return "border-blue-500 bg-blue-50 text-blue-800";
    }
  };

  return (
    <div className="fixed top-4 right-4 z-[10001] space-y-2 max-w-md">
      {notifications.map((notification) => (
        <Alert
          key={notification.id}
          variant={getVariant(notification.type)}
          className={`${getColorClasses(
            notification.type
          )} shadow-lg animate-in slide-in-from-right-2`}
        >
          {getIcon(notification.type)}
          <AlertDescription className="pr-6">
            {notification.message}
          </AlertDescription>
          <Button
            variant="ghost"
            size="sm"
            className="absolute top-2 right-2 h-6 w-6 p-0"
            onClick={() => onRemove(notification.id)}
          >
            <X className="h-3 w-3" />
          </Button>
        </Alert>
      ))}
    </div>
  );
};

export default NotificationComponent;
