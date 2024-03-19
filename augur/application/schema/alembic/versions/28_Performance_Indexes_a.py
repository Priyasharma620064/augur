""" Updating materialized views and associated indices

Revision ID: 28
Revises: 27
Create Date: 2023-08-23 18:17:22.651191

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = '28'
down_revision = '27'
branch_labels = None
depends_on = None

def upgrade():

    mview_keys_28()

def mview_keys_28(upgrade=True):

   if upgrade:
      conn = op.get_bind() 
      conn.execute(text("""
                        
      DROP INDEX if exists "pr_ID_prs_table"; 
      DROP INDEX if exists "pr_id_pr_files"; 
      DROP INDEX if exists "pr_id_pr_reviews"; 
      DROP materialized view if exists augur_data.explorer_repo_languages; 
 
                        
      
      CREATE INDEX "pr_ID_prs_table" ON "augur_data"."pull_requests" USING btree (
       "pull_request_id" "pg_catalog"."int8_ops" ASC NULLS LAST
        );

        CREATE INDEX "pr_id_pr_files" ON "augur_data"."pull_request_files" USING btree (
        "pull_request_id" "pg_catalog"."int8_ops" ASC NULLS LAST
        );

        CREATE INDEX "pr_id_pr_reviews" ON "augur_data"."pull_request_reviews" USING btree (
        "pull_request_id" "pg_catalog"."int8_ops" ASC NULLS LAST
        );"""))

      conn = op.get_bind() 
      conn.execute(text("""
        CREATE MATERIALIZED VIEW augur_data.explorer_repo_languages as 
        SELECT e.repo_id,
            repo.repo_git,
            repo.repo_name,
            e.programming_language,
            e.code_lines,
            e.files
          FROM augur_data.repo,
            ( SELECT d.repo_id,
                    d.programming_language,
                    sum(d.code_lines) AS code_lines,
                    (count(*))::integer AS files
                  FROM ( SELECT repo_labor.repo_id,
                            repo_labor.programming_language,
                            repo_labor.code_lines
                          FROM augur_data.repo_labor,
                            ( SELECT repo_labor_1.repo_id,
                                    max(repo_labor_1.data_collection_date) AS last_collected
                                  FROM augur_data.repo_labor repo_labor_1
                                  GROUP BY repo_labor_1.repo_id) recent
                          WHERE ((repo_labor.repo_id = recent.repo_id) AND (repo_labor.data_collection_date > (recent.last_collected - ((5)::double precision * '00:01:00'::interval))))) d
                  GROUP BY d.repo_id, d.programming_language) e
          WHERE (repo.repo_id = e.repo_id)
          ORDER BY e.repo_id;"""))

      conn.execute(text("""COMMIT;"""))

      conn = op.get_bind()
      conn.execute(text("""
        CREATE UNIQUE INDEX ON augur_data.explorer_repo_languages(repo_id, programming_language); """)) 
      conn.execute(text("""COMMIT;"""))
def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    conn = op.get_bind()

    #Make unique initially deferred
    conn.execute(text(f"""
      DROP INDEX if exists "pr_ID_prs_table"; 
      DROP INDEX if exists "pr_id_pr_files"; 
      DROP INDEX if exists "pr_id_pr_reviews"; 
      DROP materialized view if exists augur_data.explorer_repo_languages; 
    """))

    # ### end Alembic commands ###
