from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector


app = Flask(__name__)
app.secret_key = 'mustika_tama_secret'

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='db_panti_mustika'
    )


# ===============================
# HALAMAN PUBLIK
# ===============================

@app.route('/')
def index():
    return render_template('publik/index.html', title='Beranda')

@app.route('/kegiatan')
def kegiatan():
    return render_template('publik/kegiatan.html', title='Kegiatan')

import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/daftar', methods=['GET','POST'])
def daftar():
    if request.method == 'POST':
        foto = request.files['foto']
        filename = None
        if foto:
            filename = secure_filename(foto.filename)
            foto.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO pendaftaran (
              nik, nama_anak, jenis_kelamin, tanggal_lahir, usia,
              asal, pendidikan, alamat,
              berkebutuhan_khusus, treatment_khusus,
              nama_wali, no_hp, alasan, foto
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            request.form['nik'],
            request.form['nama_anak'],
            request.form['jenis_kelamin'],
            request.form['tanggal_lahir'],
            request.form['usia'],
            request.form['asal'],
            request.form['pendidikan'],
            request.form['alamat'],
            request.form['berkebutuhan_khusus'],
            request.form.get('treatment_khusus'),
            request.form['nama_wali'],
            request.form['no_hp'],
            request.form['alasan'],
            filename
        ))

        conn.commit()
        cur.close()
        conn.close()

        flash('Pendaftaran berhasil dikirim', 'success')
        return redirect(url_for('daftar'))

    return render_template('publik/daftar.html')




# ===============================
# LOGIN ADMIN
# ===============================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute(
            "SELECT * FROM admin WHERE username=%s AND password=%s",
            (username, password)
        )
        admin = cur.fetchone()

        cur.close()
        conn.close()

        if admin:
            session['admin'] = True
            return redirect(url_for('dashboard'))

    return render_template('auth/login.html', title='Login Admin')


# ===============================
# DASHBOARD ADMIN
# ===============================

@app.route('/admin/dashboard')
def dashboard():
    if 'admin' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    # TOTAL PENGHUNI
    cur.execute("SELECT COUNT(*) AS total FROM penghuni")
    penghuni = cur.fetchone()['total']

    # PENDAFTARAN
    cur.execute("SELECT COUNT(*) AS total FROM pendaftaran WHERE status='menunggu'")
    menunggu = cur.fetchone()['total']

    cur.execute("SELECT COUNT(*) AS total FROM pendaftaran WHERE status='disetujui'")
    disetujui = cur.fetchone()['total']

    cur.execute("SELECT COUNT(*) AS total FROM pendaftaran WHERE status='ditolak'")
    ditolak = cur.fetchone()['total']

    # DONATUR (UNIK & PAID)
    cur.execute("""
        SELECT COUNT(DISTINCT email) AS total
        FROM donasi
        WHERE status='paid'
    """)
    donatur = cur.fetchone()['total']

    # TOTAL DONASI
    cur.execute("""
        SELECT COALESCE(SUM(jumlah),0) AS total
        FROM donasi
        WHERE status='paid'
    """)
    total_donasi = cur.fetchone()['total']

    # STATUS DONASI
    cur.execute("""
        SELECT status, COUNT(*) AS total
        FROM donasi
        GROUP BY status
    """)
    status_donasi = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        'admin/dashboard.html',
        penghuni=penghuni,
        menunggu=menunggu,
        disetujui=disetujui,
        ditolak=ditolak,
        donatur=donatur,
        total_donasi=total_donasi,
        status_donasi=status_donasi
    )



# ===============================
# DAFTAR
# ===============================
@app.route('/admin/pendaftaran')
def admin_pendaftaran():
    if 'admin' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT * FROM pendaftaran
        WHERE status='menunggu'
        ORDER BY created_at DESC
    """)
    data = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('admin/pendaftaran.html', data=data)


@app.route('/admin/pendaftaran/<int:id>')
def detail_pendaftaran(id):
    if 'admin' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM pendaftaran WHERE id=%s", (id,))
    p = cur.fetchone()

    cur.close()
    conn.close()

    if not p:
        flash('Data tidak ditemukan', 'danger')
        return redirect(url_for('admin_pendaftaran'))

    return render_template('admin/pendaftaran_detail.html', p=p)



# ===============================
# PERSETUJUAN PENDAFTARAN
# ===============================
@app.route('/admin/pendaftaran/setujui/<int:id>', methods=['POST'])
def setujui_pendaftaran(id):
    if 'admin' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    # ambil data pendaftaran
    cur.execute("SELECT * FROM pendaftaran WHERE id=%s", (id,))
    p = cur.fetchone()

    if not p:
        flash('Data tidak ditemukan', 'danger')
        return redirect(url_for('admin_pendaftaran'))

    # masukkan ke penghuni
    cur.execute("""
        INSERT INTO penghuni (
            nik, nama_anak, jenis_kelamin, tanggal_lahir, usia,
            asal, pendidikan, alamat,
            berkebutuhan_khusus, treatment_khusus,
            nama_wali, no_hp, foto
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        p['nik'],
        p['nama_anak'],
        p['jenis_kelamin'],
        p['tanggal_lahir'],
        p['usia'],
        p['asal'],
        p['pendidikan'],
        p['alamat'],
        p['berkebutuhan_khusus'],
        p['treatment_khusus'],
        p['nama_wali'],
        p['no_hp'],
        p['foto']
    ))

    # update status pendaftaran
    cur.execute("""
        UPDATE pendaftaran
        SET status='disetujui'
        WHERE id=%s
    """, (id,))

    conn.commit()
    cur.close()
    conn.close()

    flash('Pendaftaran disetujui dan anak menjadi penghuni aktif', 'success')
    return redirect(url_for('admin_penghuni'))


@app.route('/admin/pendaftaran/tolak/<int:id>', methods=['POST'])
def tolak_pendaftaran(id):
    if 'admin' not in session:
        return redirect(url_for('login'))

    alasan = request.form.get('catatan_admin')

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE pendaftaran
        SET status='ditolak',
            catatan_admin=%s
        WHERE id=%s
    """, (alasan, id))

    conn.commit()
    cur.close()
    conn.close()

    flash('Pendaftaran ditolak', 'warning')
    return redirect(url_for('admin_pendaftaran'))


# ===============================
# PENGHUNI
# ===============================

@app.route('/admin/penghuni')
def admin_penghuni():
    if 'admin' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
    SELECT * FROM penghuni
    ORDER BY nama_anak
    """)
    data = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('admin/penghuni.html', data=data)


@app.route('/admin/penghuni/detail/<int:id>')
def penghuni_detail(id):
    if 'admin' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM penghuni WHERE id=%s", (id,))
    p = cur.fetchone()

    cur.close()
    conn.close()

    if not p:
        flash('Data penghuni tidak ditemukan', 'danger')
        return redirect(url_for('admin_penghuni'))

    return render_template('admin/penghuni_detail.html', p=p)



# ===============================
# CRUD PENGHUNI
# ==============================
@app.route('/admin/penghuni/tambah', methods=['GET', 'POST'])
def tambah_penghuni():
    if 'admin' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO penghuni 
            (nama, jenis_kelamin, tanggal_lahir, asal, pendidikan, tanggal_masuk, keterangan)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            request.form['nama'],
            request.form['jenis_kelamin'],
            request.form['tanggal_lahir'],
            request.form['asal'],
            request.form['pendidikan'],
            request.form['tanggal_masuk'],
            request.form['keterangan']
        ))

        conn.commit()
        cur.close()
        conn.close()

        flash('Data penghuni berhasil ditambahkan', 'success')
        return redirect(url_for('admin_penghuni'))

    return render_template('admin/tambah_penghuni.html')


@app.route('/admin/penghuni/edit/<int:id>', methods=['GET', 'POST'])
def edit_penghuni(id):
    if 'admin' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    # ambil data lama
    cur.execute("SELECT * FROM penghuni WHERE id=%s", (id,))
    p = cur.fetchone()

    if not p:
        flash('Data penghuni tidak ditemukan', 'danger')
        return redirect(url_for('admin_penghuni'))

    if request.method == 'POST':
        foto = request.files.get('foto')
        filename = p['foto']  # default foto lama

        # jika upload foto baru
        if foto and foto.filename != '':
            if allowed_file(foto.filename):
                filename = secure_filename(foto.filename)
                foto.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        cur.execute("""
            UPDATE penghuni SET
                nik=%s,
                nama_anak=%s,
                jenis_kelamin=%s,
                tanggal_lahir=%s,
                usia=%s,
                asal=%s,
                pendidikan=%s,
                alamat=%s,
                berkebutuhan_khusus=%s,
                treatment_khusus=%s,
                nama_wali=%s,
                no_hp=%s,
                alasan=%s,
                foto=%s
            WHERE id=%s
        """, (
            request.form['nik'],
            request.form['nama_anak'],
            request.form['jenis_kelamin'],
            request.form['tanggal_lahir'],
            request.form['usia'],
            request.form['asal'],
            request.form['pendidikan'],
            request.form['alamat'],
            request.form['berkebutuhan_khusus'],
            request.form.get('treatment_khusus'),
            request.form['nama_wali'],
            request.form['no_hp'],
            request.form['alasan'],
            filename,
            id
        ))

        conn.commit()
        cur.close()
        conn.close()

        flash('Data penghuni berhasil diperbarui', 'success')
        return redirect(url_for('penghuni_detail', id=id))

    cur.close()
    conn.close()
    return render_template('admin/edit_penghuni.html', p=p)


@app.route('/admin/penghuni/hapus/<int:id>', methods=['POST'])
def hapus_penghuni(id):
    if 'admin' not in session:
        return redirect(url_for('login'))

    alasan = request.form['alasan_keluar']
    keterangan = request.form.get('keterangan')

    conn = get_db_connection()
    cur = conn.cursor()

    # simpan ke mantan_penghuni
    cur.execute("""
        INSERT INTO mantan_penghuni
        (penghuni_id, alasan_keluar, keterangan, tanggal_keluar)
        VALUES (%s,%s,%s,CURDATE())
    """, (id, alasan, keterangan))

    # jika adopsi
    if alasan == 'diadopsi':
        cur.execute("""
            INSERT INTO adopsi
            (
                penghuni_id,
                nama_wali_adopsi,
                nik_wali_adopsi,
                alamat_wali,
                no_hp,
                pekerjaan,
                status_pernikahan,
                tanggal_adopsi,
                no_sk_adopsi,
                instansi_pengesah
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            id,
            request.form['nama_wali_adopsi'],
            request.form['nik_wali_adopsi'],
            request.form['alamat_wali'],
            request.form['no_hp_wali'],
            request.form['pekerjaan'],
            request.form['status_pernikahan'],
            request.form['tanggal_adopsi'],
            request.form['no_sk_adopsi'],
            request.form['instansi_pengesah']
        ))

    # update status penghuni
    cur.execute("DELETE FROM penghuni WHERE id=%s", (id,))

    conn.commit()
    cur.close()
    conn.close()

    flash('Penghuni dipindahkan ke mantan penghuni', 'success')
    return redirect(url_for('admin_penghuni'))



@app.route('/admin/mantan-penghuni')
def mantan_penghuni():
    if 'admin' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT mp.*, p.nama_anak
        FROM mantan_penghuni mp
        JOIN penghuni p ON mp.penghuni_id = p.id
        ORDER BY mp.tanggal_keluar DESC
    """)
    data = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('admin/mantan_penghuni.html', data=data)


# ===============================
# DONASI PUBLIK
# ===============================

import midtransclient

MIDTRANS_SERVER_KEY = "Mid-server-3gOJhSRDyu0f-E9oTklvdo29"
MIDTRANS_CLIENT_KEY = "Mid-client-x4QCakNlNcmz7QIj"


@app.route('/donasi', methods=['GET','POST'])
def donasi():
    if request.method == 'POST':
        anonim = 1 if request.form.get('anonim') else 0

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO donasi
            (nama_donatur, anonim, kota, no_hp, email, jumlah, doa, status)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            request.form.get('nama_donatur'),
            anonim,
            request.form.get('kota'),
            request.form.get('no_hp'),
            request.form.get('email'),
            request.form.get('jumlah'),
            request.form.get('doa'),
            'pending'
        ))

        donasi_id = cur.lastrowid

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('checkout_donasi', id=donasi_id))

    return render_template('publik/donasi.html')


@app.route('/donasi/checkout/<int:id>')
def checkout_donasi(id):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM donasi WHERE id=%s", (id,))
    donasi = cur.fetchone()

    cur.close()
    conn.close()

    return render_template(
        'publik/checkout.html',
        donasi=donasi,
        midtrans_client_key=MIDTRANS_CLIENT_KEY
    )


@app.route('/donasi/bayar/<int:id>', methods=['POST'])
def bayar_donasi(id):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM donasi WHERE id=%s", (id,))
    donasi = cur.fetchone()

    if not donasi:
        return {"error": "Donasi tidak ditemukan"}, 404

    snap = midtransclient.Snap(
        is_production=False,
        server_key=MIDTRANS_SERVER_KEY
    )

    param = {
        "transaction_details": {
            "order_id": f"DONASI-{donasi['id']}",
            "gross_amount": int(donasi['jumlah'])
        },
        "customer_details": {
            "first_name": "Hamba Allah" if donasi['anonim'] else donasi['nama_donatur'],
            "email": donasi['email'] or "donatur@example.com",
            "phone": donasi['no_hp']
        }
    }

    try:
        transaction = snap.create_transaction(param)
    except Exception as e:
        return {"error": str(e)}, 500

    # simpan order_id
    cur.execute(
        "UPDATE donasi SET order_id=%s WHERE id=%s",
        (param["transaction_details"]["order_id"], id)
    )
    conn.commit()

    cur.close()
    conn.close()

    return {"snap_token": transaction["token"]}


@app.route('/midtrans/callback', methods=['POST'])
def midtrans_callback():
    data = request.json
    order_id = data['order_id']
    status = data['transaction_status']

    donasi_id = order_id.replace('DONASI-', '')

    conn = get_db_connection()
    cur = conn.cursor()

    if status in ['settlement', 'capture']:
        cur.execute("""
            UPDATE donasi 
            SET status='paid' 
            WHERE id=%s
        """, (donasi_id,))
    elif status in ['pending']:
        cur.execute("""
            UPDATE donasi 
            SET status='pending' 
            WHERE id=%s
        """, (donasi_id,))
    else:
        cur.execute("""
            UPDATE donasi 
            SET status='failed' 
            WHERE id=%s
        """, (donasi_id,))

    conn.commit()
    cur.close()
    conn.close()

    return {"status": "ok"}


@app.route('/donasi/sukses/<int:id>')
def donasi_sukses(id):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM donasi WHERE id=%s", (id,))
    donasi = cur.fetchone()

    cur.close()
    conn.close()

    return render_template('publik/donasi_sukses.html', donasi=donasi)


# ===============================
# DONASI
# ===============================
@app.route('/admin/donasi')
def admin_donasi():
    status = request.args.get('status')

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    # status yang diizinkan (whitelist)
    allowed_status = ['paid', 'pending', 'failed', 'expired']

    if status in allowed_status:
        cur.execute("""
            SELECT *
            FROM donasi
            WHERE status = %s
            ORDER BY created_at DESC
        """, (status,))
    else:
        # default: tampilkan semua
        cur.execute("""
            SELECT *
            FROM donasi
            ORDER BY created_at DESC
        """)

    donasi = cur.fetchall()

    # ===== SUMMARY UNTUK DASHBOARD =====
    cur.execute("""
        SELECT 
            COUNT(*) AS total_transaksi,
            COALESCE(SUM(CASE WHEN status='paid' THEN jumlah ELSE 0 END),0) AS total_paid,
            COUNT(CASE WHEN status='paid' THEN 1 END) AS paid_count,
            COUNT(CASE WHEN status='pending' THEN 1 END) AS pending_count,
            COUNT(CASE WHEN status='failed' THEN 1 END) AS failed_count
        FROM donasi
    """)
    summary = cur.fetchone()

    cur.close()
    conn.close()

    return render_template(
        'admin/donasi_dashboard.html',
        donasi=donasi,
        status=status,
        summary=summary
    )




# ===============================
# LOGOUT
# ===============================
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ===============================
# MAIN
# ===============================

if __name__ == '__main__':
    app.run(debug=True)
