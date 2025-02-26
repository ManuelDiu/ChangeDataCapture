-- add modified_by, modified_at columns
ALTER TABLE transactions add column modified_by TEXT;
ALTER TABLE transactions add column modified_at TIMESTAMP;


CREATE OR REPLACE FUNCTION record_change_user()
RETURNS TRIGGER AS $$
BEGIN
    NEW.modified_by := current_user;
    NEW.modified_at := CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for UPDATE
CREATE TRIGGER trigger_record_user_update
BEFORE UPDATE ON transactions
FOR EACH ROW EXECUTE FUNCTION record_change_user();

-- capture before records on debezium
ALTER TABLE transactions REPLICA IDENTITY FULL;

-- add change information column
ALTER TABLE transactions ADD COLUMN change_info JSONB;


CREATE OR REPLACE FUNCTION record_changed_columns()
RETURNS TRIGGER AS $$
DECLARE
change_details JSONB;
BEGIN
    change_details := '{}'::JSONB; -- empty json object

    IF NEW.amount IS DISTINCT FROM OLD.amount THEN
        change_details := jsonb_set(
            change_details,
            '{amount}',
            jsonb_build_object('old', OLD.amount, 'new', NEW.amount)
        );
    END IF;

    -- add the user and the timestamp
    change_details := change_details || jsonb_build_object('modified_by', current_user, 'modified_at', now());

    -- Update the change_info column
    NEW.change_info := change_details;
RETURN NEW;
END;
$$
LANGUAGE plpgsql;


create trigger trigger_record_change_info
before update
    on transactions
    for each row execute function record_changed_columns();
