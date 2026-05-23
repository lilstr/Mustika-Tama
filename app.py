from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import mysql.connector
import os
import random
import smtplib
from email.mime.text import MIMEText
from werkzeug.security import generate_password_hash, check_password_hash
from report_generator import (
    generate_penghuni_excel, generate_penghuni_pdf,
    generate_donasi_excel, generate_donasi_pdf
)
from datetime import datetime, timedelta


def load_env(path='.env'):
    if not os.path.exists(path):
        return
    with open(path, 'r', encoding='utf-8') as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


load_env()

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'mustika_tama_secret')

# Email configuration for OTP reset
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 25))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'andarisbintang16@gmail.com')
# PERUBAHAN: Baca dari System Environment Variable saja
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'False').lower() in ('1', 'true', 'yes')
EMAIL_FROM = os.environ.get('EMAIL_FROM', 'andarisbintang16@gmail.com')

def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        user=os.environ.get('DB_USER', 'root'),
        password=os.environ.get('DB_PASSWORD', ''),
        database=os.environ.get('DB_NAME', 'db_panti_mustika')
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

@app.route('/daftar-overview')
def daftar_overview():
    return render_template('publik/daftar_overview.html', title='Pendaftaran')

import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_otp(length=6):
    return ''.join(random.choices('0123456789', k=length))


def send_email(subject, body, recipient):
    # For development: print to console instead of sending email
    if EMAIL_HOST.lower() == 'console':
        print(f"\n=== EMAIL SIMULATION ===")
        print(f"To: {recipient}")
        print(f"Subject: {subject}")
        print(f"Body:\n{body}")
        print("=" * 50)

        # Also save to file for debugging
        try:
            with open('otp_debug.txt', 'w') as f:
                f.write(f'Latest OTP sent to: {recipient}\n')
                f.write(f'Subject: {subject}\n')
                f.write(f'Body:\n{body}\n')
                f.write('=' * 50 + '\n')
                f.write('Check this file for OTP codes during testing.\n')
        except:
            pass

        return True

    # Check if EMAIL_HOST_PASSWORD exists
    if not EMAIL_HOST_PASSWORD:
        print("ERROR: EMAIL_HOST_PASSWORD not set in System Environment Variables!")
        print("Set it using: setx EMAIL_HOST_PASSWORD \"your_password\"")
        return False

    # Always save to debug file for troubleshooting
    try:
        with open('otp_debug.txt', 'w') as f:
            f.write(f'Latest OTP sent to: {recipient}\n')
            f.write(f'Subject: {subject}\n')
            f.write(f'Body:\n{body}\n')
            f.write('=' * 50 + '\n')
            f.write('Attempting to send via SMTP...\n')
    except:
        pass

    msg = MIMEText(body, 'plain', 'utf-8')
    msg['Subject'] = subject
    msg['From'] = EMAIL_FROM
    msg['To'] = recipient

    try:
        if EMAIL_PORT == 465:
            server = smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT, timeout=10)
        else:
            server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=10)
            if EMAIL_USE_TLS:
                server.starttls()

        if EMAIL_HOST_USER and EMAIL_HOST_PASSWORD:
            server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)

        server.sendmail(EMAIL_FROM, [recipient], msg.as_string())
        server.quit()
        
        # Update debug file on success
        try:
            with open('otp_debug.txt', 'a') as f:
                f.write('SMTP send successful.\n')
        except:
            pass
        
        return True
    except Exception as e:
        print(f"Email error: {e}")
        
        # Update debug file on failure
        try:
            with open('otp_debug.txt', 'a') as f:
                f.write(f'SMTP send failed: {e}\n')
        except:
            pass
        
        return False


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
        email_or_username = request.form['email_or_username'].strip()
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)

        try:
            cur.execute(
                "SELECT * FROM admin WHERE email=%s OR username=%s",
                (email_or_username, email_or_username)
            )
        except mysql.connector.Error:
            cur.execute("SELECT * FROM admin WHERE username=%s", (email_or_username,))

        admin = cur.fetchone()
        cur.close()
        conn.close()

        if admin and check_password_hash(admin['password'], password):
            session['admin'] = True
            return redirect(url_for('dashboard'))

        flash('Email atau password salah.', 'danger')

    return render_template('auth/login.html', title='Login Admin')


@app.route('/admin/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email'].strip()

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)

        try:
            cur.execute("SELECT * FROM admin WHERE email=%s", (email,))
            admin = cur.fetchone()
        except mysql.connector.Error:
            admin = None

        cur.close()
        conn.close()

        if not admin:
            flash('Alamat email tidak terdaftar.', 'danger')
            return render_template('auth/forgot_password.html', title='Lupa Password')

        otp = generate_otp()
        expiry = datetime.now() + timedelta(minutes=10)
        session['password_reset'] = {
            'email': email,
            'otp': otp,
            'expires_at': expiry.isoformat()
        }

        subject = 'Kode OTP Reset Password Admin'
        body = (
            f'Anda menerima permintaan reset password untuk akun admin.\n\n'
            f'Kode OTP Anda adalah: {otp}\n'
            f'Kode ini berlaku selama 10 menit.\n\n'
            'Jika Anda tidak meminta reset, abaikan email ini.'
        )

        if send_email(subject, body, email):
            flash('Kode OTP telah dikirim ke email Anda. Silakan periksa kotak masuk.', 'success')
            return redirect(url_for('verify_otp'))

        flash('Gagal mengirim email OTP. Periksa konfigurasi email.', 'danger')

    return render_template('auth/forgot_password.html', title='Lupa Password')


@app.route('/admin/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    reset_data = session.get('password_reset')
    if not reset_data:
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        otp_input = request.form['otp'].strip()
        expires_at = datetime.fromisoformat(reset_data['expires_at'])

        if datetime.now() > expires_at:
            session.pop('password_reset', None)
            flash('Kode OTP telah kedaluwarsa. Silakan minta ulang.', 'danger')
            return redirect(url_for('forgot_password'))

        if otp_input != reset_data['otp']:
            flash('Kode OTP salah. Silakan coba lagi.', 'danger')
            return render_template('auth/verify_otp.html', title='Verifikasi OTP')

        session['password_reset_verified'] = True
        flash('OTP berhasil diverifikasi. Silakan buat password baru.', 'success')
        return redirect(url_for('reset_password'))

    return render_template('auth/verify_otp.html', title='Verifikasi OTP')


@app.route('/admin/reset-password', methods=['GET', 'POST'])
def reset_password():
    reset_data = session.get('password_reset')
    if not reset_data or not session.get('password_reset_verified'):
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Password tidak cocok.', 'danger')
            return render_template('auth/reset_password.html', title='Reset Password')

        hashed_password = generate_password_hash(password)
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE admin SET password=%s WHERE email=%s",
            (hashed_password, reset_data['email'])
        )
        conn.commit()
        cur.close()
        conn.close()

        session.pop('password_reset', None)
        session.pop('password_reset_verified', None)

        flash('Password berhasil diperbarui. Silakan login.', 'success')
        return redirect(url_for('login'))

    return render_template('auth/reset_password.html', title='Reset Password')


# ===============================
# DASHBOARD ADMIN
# ===============================

@app.route('/admin/dashboard')
def dashboard():
    if 'admin' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    # TOTAL PENGHUNI (hanya penghuni aktif, tidak termasuk mantan penghuni)
    cur.execute("""
        SELECT COUNT(p.id) AS total
        FROM penghuni p
        LEFT JOIN mantan_penghuni mp ON mp.penghuni_id = p.id
        WHERE mp.penghuni_id IS NULL
    """)
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
            nama_wali, no_hp, alasan, foto, tanggal_masuk
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,CURDATE())
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
        p['alasan'],
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

    # Build query with search filters
    query = """
    SELECT p.* FROM penghuni p
    LEFT JOIN mantan_penghuni mp ON mp.penghuni_id = p.id
    WHERE mp.penghuni_id IS NULL
    """
    params = []

    search = request.args.get('search', '').strip()
    jenis_kelamin = request.args.get('jenis_kelamin', '')

    if search:
        query += """ AND (nama_anak LIKE %s OR nik LIKE %s OR asal LIKE %s OR nama_wali LIKE %s)"""
        search_param = f"%{search}%"
        params.extend([search_param, search_param, search_param, search_param])

    if jenis_kelamin:
        query += " AND jenis_kelamin = %s"
        params.append(jenis_kelamin)

    query += " ORDER BY nama_anak"

    cur.execute(query, params)
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
        foto = request.files['foto']
        filename = None
        if foto:
            filename = secure_filename(foto.filename)
            foto.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO penghuni (
              nik, nama_anak, jenis_kelamin, tanggal_lahir, usia,
              asal, pendidikan, alamat,
              berkebutuhan_khusus, treatment_khusus,
              nama_wali, no_hp, alasan, foto, tanggal_masuk
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,CURDATE())
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
    keterangan = request.form.get('keterangan', '')

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    # ambil data penghuni terlebih dahulu untuk mendapatkan nama_anak
    cur.execute("SELECT nama_anak, no_hp FROM penghuni WHERE id=%s", (id,))
    penghuni = cur.fetchone()

    if not penghuni:
        flash('Penghuni tidak ditemukan', 'error')
        return redirect(url_for('admin_penghuni'))

    no_hp_wali = penghuni['no_hp']

    # hapus record lama dari mantan_penghuni jika ada
    cur.execute("DELETE FROM mantan_penghuni WHERE penghuni_id=%s", (id,))
    cur.execute("DELETE FROM adopsi WHERE penghuni_id=%s", (id,))

    # ambil data adopsi jika alasan adalah diadopsi
    nama_wali_adopsi = ''
    nik_wali_adopsi = ''
    alamat_wali = ''
    pekerjaan = ''
    status_pernikahan = ''
    hubungan_dengan_anak = 'Tidak ada'
    tanggal_adopsi = None
    no_sk_adopsi = ''
    instansi_pengesah = ''
    catatan = ''

    if alasan == 'diadopsi':
        nama_wali_adopsi = request.form.get('nama_wali_adopsi', '')
        nik_wali_adopsi = request.form.get('nik_wali_adopsi', '')
        alamat_wali = request.form.get('alamat_wali', '')
        pekerjaan = request.form.get('pekerjaan', '')
        status_pernikahan = request.form.get('status_pernikahan', '')
        hubungan_dengan_anak = request.form.get('hubungan_dengan_anak', '')
        tanggal_adopsi = request.form.get('tanggal_adopsi')
        no_sk_adopsi = request.form.get('no_sk_adopsi', '')
        instansi_pengesah = request.form.get('instansi_pengesah', '')
        catatan = request.form.get('catatan', '')

        # insert ke tabel adopsi
        cur.execute("""
            INSERT INTO adopsi (
                penghuni_id, nama_wali_adopsi, nik_wali_adopsi, alamat_wali,
                no_hp, pekerjaan, status_pernikahan, hubungan_dengan_anak,
                tanggal_adopsi, no_sk_adopsi, instansi_pengesah
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            id, nama_wali_adopsi, nik_wali_adopsi, alamat_wali,
            no_hp_wali, pekerjaan, status_pernikahan, hubungan_dengan_anak,
            tanggal_adopsi, no_sk_adopsi, instansi_pengesah
        ))

    # simpan ke mantan_penghuni
    cur.execute("""
        INSERT INTO mantan_penghuni
        (penghuni_id, nama_anak, alasan_keluar, keterangan, tanggal_keluar,
         nama_wali_adopsi, nik_wali_adopsi, alamat_wali, no_hp_wali, pekerjaan,
         status_pernikahan, hubungan_dengan_anak, tanggal_adopsi, no_sk_adopsi,
         instansi_pengesah)
        VALUES (%s,%s,%s,%s,CURDATE(),
                %s,%s,%s,%s,%s,
                %s,%s,%s,%s,%s)
    """, (id, penghuni['nama_anak'], alasan, keterangan,
          nama_wali_adopsi, nik_wali_adopsi, alamat_wali, no_hp_wali, pekerjaan,
          status_pernikahan, hubungan_dengan_anak, tanggal_adopsi, no_sk_adopsi,
          instansi_pengesah))

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

    # Build query with search filters
    query = """
        SELECT mp.*, p.nama_anak, p.jenis_kelamin, p.usia, p.asal
        FROM mantan_penghuni mp
        JOIN penghuni p ON mp.penghuni_id = p.id
    """
    params = []

    search = request.args.get('search', '').strip()
    jenis_kelamin = request.args.get('jenis_kelamin', '')
    alasan_keluar = request.args.get('alasan_keluar', '')

    if search:
        query += """ WHERE (p.nama_anak LIKE %s OR p.nik LIKE %s OR p.asal LIKE %s OR p.nama_wali LIKE %s OR mp.alasan_keluar LIKE %s)"""
        search_param = f"%{search}%"
        params.extend([search_param, search_param, search_param, search_param, search_param])

    if jenis_kelamin:
        if search:
            query += " AND p.jenis_kelamin = %s"
        else:
            query += " WHERE p.jenis_kelamin = %s"
        params.append(jenis_kelamin)

    if alasan_keluar:
        if search or jenis_kelamin:
            query += " AND mp.alasan_keluar = %s"
        else:
            query += " WHERE mp.alasan_keluar = %s"
        params.append(alasan_keluar)

    query += " ORDER BY mp.tanggal_keluar DESC"

    cur.execute(query, params)
    data = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('admin/mantan_penghuni.html', data=data)

@app.route('/admin/mantan-penghuni/<int:id>')
def mantan_penghuni_detail(id):
    if 'admin' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    # Get mantan penghuni data with penghuni details
    cur.execute("""
        SELECT mp.*, 
               p.id as penghuni_id_orig,
               p.nama_anak, p.jenis_kelamin, p.nik, p.tanggal_lahir, 
               p.usia, p.asal, p.pendidikan, p.alamat, 
               p.berkebutuhan_khusus, p.treatment_khusus,
               p.nama_wali, p.no_hp, p.foto
        FROM mantan_penghuni mp
        JOIN penghuni p ON mp.penghuni_id = p.id
        WHERE mp.id = %s
    """, (id,))
    m = cur.fetchone()

    if not m:
        cur.close()
        conn.close()
        return redirect(url_for('mantan_penghuni'))

    cur.close()
    conn.close()

    return render_template('admin/mantan_penghuni_detail.html', m=m)


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

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT id, nama_donatur, anonim, kota, jumlah, doa, status, created_at
        FROM donasi
        WHERE status='paid'
        ORDER BY created_at DESC
        LIMIT 10
    """
    )
    recent_donatur = cur.fetchall()

    cur.execute("""
        SELECT COUNT(*) AS total_donatur, IFNULL(SUM(jumlah), 0) AS total_donasi
        FROM donasi
        WHERE status='paid'
    """)
    stats = cur.fetchone() or {'total_donatur': 0, 'total_donasi': 0}
    total_donatur = stats['total_donatur']
    total_donasi = stats['total_donasi']

    cur.execute("""
        SELECT nama_donatur, anonim, kota, doa, created_at
        FROM donasi
        WHERE status='paid' AND doa IS NOT NULL AND doa <> ''
        ORDER BY created_at DESC
        LIMIT 4
    """)
    testimonial_donatur = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        'publik/donasi.html',
        recent_donatur=recent_donatur,
        total_donatur=total_donatur,
        total_donasi=total_donasi,
        testimonial_donatur=testimonial_donatur
    )


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
    import time
    
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

    # Generate unique order_id dengan timestamp
    timestamp = int(time.time() * 1000)
    order_id = f"DONASI-{donasi['id']}-{timestamp}"

    param = {
        "transaction_details": {
            "order_id": order_id,
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
        (order_id, id)
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
# DONASI ADMIN
# ===============================
@app.route('/admin/donasi')
def admin_donasi():
    if 'admin' not in session:
        return redirect(url_for('login'))
    
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
# LAPORAN / REPORT
# ===============================

@app.route('/admin/laporan/penghuni')
def laporan_penghuni():
    if 'admin' not in session:
        return redirect(url_for('login'))
    
    return render_template('admin/laporan_penghuni.html')


@app.route('/admin/laporan/donasi')
def laporan_donasi():
    if 'admin' not in session:
        return redirect(url_for('login'))
    
    return render_template('admin/laporan_donasi.html')


@app.route('/admin/download/penghuni/<format>', methods=['GET'])
def download_penghuni(format):
    if 'admin' not in session:
        return redirect(url_for('login'))
    
    period_type = request.args.get('period', 'all')
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', 1, type=int)
    
    try:
        if format == 'excel':
            output = generate_penghuni_excel(period_type, year, month)
            
            if period_type == 'yearly':
                filename = f"Laporan_Penghuni_{year}.xlsx"
            elif period_type == 'monthly':
                month_names = ['', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
                              'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
                filename = f"Laporan_Penghuni_{month_names[month]}_{year}.xlsx"
            else:
                filename = f"Laporan_Penghuni_Semua_{datetime.now().strftime('%d%m%Y')}.xlsx"
            
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=filename
            )
        
        elif format == 'pdf':
            output = generate_penghuni_pdf(period_type, year, month)
            
            if period_type == 'yearly':
                filename = f"Laporan_Penghuni_{year}.pdf"
            elif period_type == 'monthly':
                month_names = ['', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
                              'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
                filename = f"Laporan_Penghuni_{month_names[month]}_{year}.pdf"
            else:
                filename = f"Laporan_Penghuni_Semua_{datetime.now().strftime('%d%m%Y')}.pdf"
            
            return send_file(
                output,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=filename
            )
    
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('laporan_penghuni'))


@app.route('/admin/download/donasi/<format>', methods=['GET'])
def download_donasi(format):
    if 'admin' not in session:
        return redirect(url_for('login'))
    
    period_type = request.args.get('period', 'all')
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', 1, type=int)
    
    try:
        if format == 'excel':
            output = generate_donasi_excel(period_type, year, month)
            
            if period_type == 'yearly':
                filename = f"Laporan_Donasi_{year}.xlsx"
            elif period_type == 'monthly':
                month_names = ['', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
                              'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
                filename = f"Laporan_Donasi_{month_names[month]}_{year}.xlsx"
            else:
                filename = f"Laporan_Donasi_Semua_{datetime.now().strftime('%d%m%Y')}.xlsx"
            
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=filename
            )
        
        elif format == 'pdf':
            output = generate_donasi_pdf(period_type, year, month)
            
            if period_type == 'yearly':
                filename = f"Laporan_Donasi_{year}.pdf"
            elif period_type == 'monthly':
                month_names = ['', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
                              'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
                filename = f"Laporan_Donasi_{month_names[month]}_{year}.pdf"
            else:
                filename = f"Laporan_Donasi_Semua_{datetime.now().strftime('%d%m%Y')}.pdf"
            
            return send_file(
                output,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=filename
            )
    
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('laporan_donasi'))

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
